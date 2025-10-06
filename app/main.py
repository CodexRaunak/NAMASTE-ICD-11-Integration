from fastapi import FastAPI
from app import conceptmap

app = FastAPI(
    title="Ayush ICD-11 Terminology Microservice",
    version="0.1.0",
    description="FHIR-compliant terminology service for mapping NAMASTE Ayurveda codes to ICD-11"
)

@app.get("/")
def root():
    return {
        "message": "AYUSH ICD-11 Terminology Microservice",
        "version": "0.1.0",
        "endpoints": {
            "concept_maps": "/ConceptMap",
            "specific_mapping": "/ConceptMap/{code}",
            "docs": "/docs"
        }
    }

# Register routers
app.include_router(conceptmap.router, tags=["ConceptMap"])
