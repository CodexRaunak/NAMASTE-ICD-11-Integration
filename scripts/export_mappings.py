#!/usr/bin/env python3
"""
Export all concept mappings to CSV file for review and analysis
"""

import sqlite3
import csv
import os
from datetime import datetime

def export_mappings_to_csv():
    """Export all concept mappings to a CSV file"""
    
    # Database path
    db_path = "db/ayush_icd11_combined.db"
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{output_dir}/namaste_icd11_mappings_{timestamp}.csv"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Querying concept mappings from database...")
        
        # Query all mappings with additional information
        query = """
        SELECT 
            cm.id,
            cm.source_system,
            cm.source_code,
            cm.target_system,
            cm.target_code,
            cm.equivalence,
            nam.namc_term as source_term,
            nam.namc_term_devanagari as source_term_devanagari,
            nam.short_definition as source_definition,
            icd11.title as target_title,
            SUBSTR(cm.source_code, 1, 2) as source_prefix,
            SUBSTR(cm.target_code, 1, 2) as target_prefix
        FROM concept_map cm
        LEFT JOIN nam ON cm.source_code = nam.namc_code
        LEFT JOIN icd11 ON cm.target_code = icd11.code
        ORDER BY cm.source_code, cm.target_code
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"📊 Found {len(rows):,} mappings to export")
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Write to CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(column_names)
            
            # Write data rows
            for row in rows:
                writer.writerow(row)
        
        conn.close()
        
        print(f"✅ Successfully exported mappings to: {csv_filename}")
        
        # Generate summary statistics
        generate_mapping_summary(csv_filename)
        
        return csv_filename
        
    except Exception as e:
        print(f"❌ Error exporting mappings: {e}")
        return None

def generate_mapping_summary(csv_filename):
    """Generate a summary report of the mappings"""
    
    summary_filename = csv_filename.replace('.csv', '_summary.txt')
    
    try:
        # Connect to database for summary queries
        conn = sqlite3.connect("db/ayush_icd11_combined.db")
        cursor = conn.cursor()
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("NAMASTE-ICD-11 MAPPING SUMMARY REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Total mappings
            cursor.execute("SELECT COUNT(*) FROM concept_map")
            total_mappings = cursor.fetchone()[0]
            f.write(f"Total Mappings: {total_mappings:,}\n\n")
            
            # Unique source codes
            cursor.execute("SELECT COUNT(DISTINCT source_code) FROM concept_map")
            unique_source = cursor.fetchone()[0]
            f.write(f"Unique NAMASTE Codes Mapped: {unique_source:,}\n")
            
            # Unique target codes
            cursor.execute("SELECT COUNT(DISTINCT target_code) FROM concept_map")
            unique_target = cursor.fetchone()[0]
            f.write(f"Unique ICD-11 Codes Targeted: {unique_target:,}\n\n")
            
            # Source prefix breakdown
            f.write("NAMASTE CODE PREFIX BREAKDOWN:\n")
            f.write("-" * 30 + "\n")
            cursor.execute("""
                SELECT SUBSTR(source_code, 1, 2) as prefix, 
                       COUNT(DISTINCT source_code) as unique_codes,
                       COUNT(*) as total_mappings
                FROM concept_map 
                GROUP BY SUBSTR(source_code, 1, 2) 
                ORDER BY prefix
            """)
            
            for prefix, unique_codes, total_mappings in cursor.fetchall():
                f.write(f"{prefix}: {unique_codes:,} codes → {total_mappings:,} mappings\n")
            
            f.write("\n")
            
            # Target prefix breakdown
            f.write("ICD-11 TM2 TARGET PREFIX BREAKDOWN:\n")
            f.write("-" * 35 + "\n")
            cursor.execute("""
                SELECT SUBSTR(target_code, 1, 2) as prefix, 
                       COUNT(DISTINCT target_code) as unique_codes,
                       COUNT(*) as total_mappings
                FROM concept_map 
                GROUP BY SUBSTR(target_code, 1, 2) 
                ORDER BY prefix
            """)
            
            for prefix, unique_codes, total_mappings in cursor.fetchall():
                f.write(f"{prefix}: {unique_codes:,} codes ← {total_mappings:,} mappings\n")
            
            f.write("\n")
            
            # Top mapped NAMASTE codes
            f.write("TOP 10 MOST MAPPED NAMASTE CODES:\n")
            f.write("-" * 35 + "\n")
            cursor.execute("""
                SELECT source_code, COUNT(*) as mapping_count
                FROM concept_map 
                GROUP BY source_code 
                ORDER BY mapping_count DESC 
                LIMIT 10
            """)
            
            for code, count in cursor.fetchall():
                f.write(f"{code}: {count:,} mappings\n")
            
            f.write("\n")
            
            # Sample mappings by prefix
            f.write("SAMPLE MAPPINGS BY PREFIX:\n")
            f.write("-" * 30 + "\n")
            cursor.execute("""
                SELECT SUBSTR(source_code, 1, 2) as prefix,
                       source_code,
                       target_code
                FROM concept_map 
                WHERE rowid IN (
                    SELECT MIN(rowid) 
                    FROM concept_map 
                    GROUP BY SUBSTR(source_code, 1, 2)
                )
                ORDER BY prefix
            """)
            
            for prefix, source, target in cursor.fetchall():
                f.write(f"{prefix}: {source} → {target}\n")
        
        conn.close()
        
        print(f"📋 Summary report generated: {summary_filename}")
        
    except Exception as e:
        print(f"⚠️  Error generating summary: {e}")

def export_sample_mappings():
    """Export a sample of mappings for quick review"""
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_filename = f"{output_dir}/namaste_icd11_sample_{timestamp}.csv"
    
    try:
        conn = sqlite3.connect("db/ayush_icd11_combined.db")
        cursor = conn.cursor()
        
        # Get 10 samples from each prefix
        query = """
        WITH prefix_samples AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY SUBSTR(source_code, 1, 2) ORDER BY source_code) as rn
            FROM concept_map cm
            LEFT JOIN nam ON cm.source_code = nam.namc_code
            LEFT JOIN icd11 ON cm.target_code = icd11.code
        )
        SELECT 
            source_code,
            target_code,
            equivalence,
            namc_term as source_term,
            title as target_title,
            SUBSTR(source_code, 1, 2) as source_prefix
        FROM prefix_samples
        WHERE rn <= 10
        ORDER BY source_prefix, source_code
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        column_names = [description[0] for description in cursor.description]
        
        with open(sample_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)
            for row in rows:
                writer.writerow(row)
        
        conn.close()
        
        print(f"📝 Sample mappings exported: {sample_filename}")
        print(f"   Contains {len(rows):,} sample mappings (10 per prefix)")
        
        return sample_filename
        
    except Exception as e:
        print(f"❌ Error exporting sample: {e}")
        return None

if __name__ == "__main__":
    print("🚀 NAMASTE-ICD-11 MAPPING EXPORT UTILITY")
    print("=" * 50)
    
    # Export full mappings
    full_export = export_mappings_to_csv()
    
    print()
    
    # Export sample mappings
    sample_export = export_sample_mappings()
    
    print()
    print("✅ Export complete!")
    if full_export:
        print(f"📊 Full export: {full_export}")
        print(f"📋 Summary: {full_export.replace('.csv', '_summary.txt')}")
    if sample_export:
        print(f"📝 Sample: {sample_export}")
    
    print("\n💡 You can now review the mappings in Excel, Google Sheets, or any CSV viewer!")