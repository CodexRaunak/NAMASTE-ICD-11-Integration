from fastapi import APIRouter, HTTPException
import sqlite3
from urllib.parse import unquote
from fhir.resources.conceptmap import ConceptMap, ConceptMapGroup, ConceptMapGroupElement, ConceptMapGroupElementTarget
from fhir.resources.bundle import Bundle, BundleEntry
from typing import List
import uuid
from datetime import datetime
import re

DB_PATH = "db/ayush_icd11_combined.db"

router = APIRouter()

def normalize_code(code: str) -> str:
    return re.sub(r"\s+", " ", code).strip()


def fetch_concept_map(source_code: str):
    source_code = normalize_code(source_code)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Try multiple search patterns to handle variations in spacing and format
    cur.execute("""
        SELECT source_code, target_code, equivalence
        FROM concept_map
        WHERE source_code = ? 
           OR source_code LIKE ?
           OR source_code LIKE ?
           OR source_code LIKE ?
    """, (source_code, f"{source_code}(%", f"{source_code} %", f"{source_code}(%"))
    
    rows = cur.fetchall()
    conn.close()
    return [(normalize_code(r[0]), r[1], r[2]) for r in rows]

def fetch_namaste_term(namc_code: str):
    """Fetch the NAMASTE term for a given code"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT namc_term FROM nam WHERE namc_code = ? LIMIT 1", (namc_code,))
    result = cur.fetchone()
    conn.close()
    
    return result[0] if result else None

def fetch_icd11_title(icd_code: str):
    """Fetch the ICD-11 title for a given code"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT title FROM icd11 WHERE code = ? LIMIT 1", (icd_code,))
    result = cur.fetchone()
    conn.close()
    
    return result[0] if result else None

@router.get("/ConceptMap")
def list_all_concept_maps():
    """List all available concept mappings as FHIR Bundle"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT source_code FROM concept_map ORDER BY source_code")
    codes = [row[0] for row in cur.fetchall()]
    conn.close()
    
    # Return simple JSON response instead of complex Bundle for listing
    return {
        "resourceType": "Bundle",
        "type": "searchset", 
        "total": len(codes),
        "available_codes": codes,
        "message": "Use /ConceptMap/{code} to get specific FHIR ConceptMap resources"
    }
    
    return bundle.dict()

@router.get("/ConceptMap/{source_code}")
def get_concept_map(source_code: str):
    """Get FHIR ConceptMap for a specific source code"""
    # URL decode the source code (handles %28 = ( and %29 = ))
    decoded_source_code = unquote(source_code)
    
    rows = fetch_concept_map(decoded_source_code)
    if not rows:
        raise HTTPException(status_code=404, detail=f"Mapping not found for code: {decoded_source_code}")

    # Build proper FHIR ConceptMap
    elements = []
    for source_code, target_code, equivalence in rows:
        # Get display names from database
        source_display = fetch_namaste_term(source_code) or f"NAMASTE code {source_code}"
        target_display = fetch_icd11_title(target_code) or f"ICD-11 code {target_code}"
        
        # Create target mapping
        # The installed FHIR model expects the field name 'relationship' rather
        # than 'equivalence' (this is a library-level naming). Use the
        # library field for validation, then post-process the serialized
        # output to emit the standard FHIR 'equivalence' key downstream.
        target = ConceptMapGroupElementTarget(
            code=target_code,
            display=target_display,
            relationship=equivalence
        )
        
        # Create element
        element = ConceptMapGroupElement(
            code=source_code,
            display=source_display,
            target=[target]
        )
        elements.append(element)
    
    # Create group
    group = ConceptMapGroup(
        source="http://namaste.terminology/CodeSystem",
        target="http://id.who.int/icd/release/11/mms",
        element=elements
    )
    
    # Create ConceptMap with proper FHIR R4 fields (no top-level source/target URIs)
    concept_map_id = f"namaste-to-icd11-{decoded_source_code.replace('(', '').replace(')', '').replace(' ', '-')}"
    
    concept_map = ConceptMap(
        id=concept_map_id,
        url=f"http://namaste.terminology/ConceptMap/{concept_map_id}",
        version="1.0.0", 
        name=f"NAMASTE_{decoded_source_code.replace('(', '_').replace(')', '_').replace(' ', '_')}_to_ICD11",
        title=f"NAMASTE {decoded_source_code} to ICD-11 TM2 Concept Mapping",
        status="active",
        date=datetime.now().date().isoformat(),
        publisher="NAMASTE-ICD-11 Integration Service",
        description=f"Concept mapping from NAMASTE Ayurveda code {decoded_source_code} to ICD-11 Traditional Medicine 2 (TM2) codes",
        # Note: No sourceUri/targetUri at top level - they go in the group
        group=[group]
    )

    # Serialize via the FHIR model (validates fields) then convert any
    # 'relationship' keys emitted by the model into FHIR-standard
    # 'equivalence' keys for downstream consumers expecting R4 naming.
    def _replace_relationship_with_equivalence(obj):
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                new_key = 'equivalence' if k == 'relationship' else k
                new[new_key] = _replace_relationship_with_equivalence(v)
            return new
        elif isinstance(obj, list):
            return [_replace_relationship_with_equivalence(i) for i in obj]
        else:
            return obj

    serialized = concept_map.dict()
    return _replace_relationship_with_equivalence(serialized)
