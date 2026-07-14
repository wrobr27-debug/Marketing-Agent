import sys
from src.database import init_db
from src.crawler import query_osm_leads
from src.analyzer import audit_all_leads
from src.generator import generate_all_pitches
from src.build_dashboard import build_dashboard

def main():
    flags = sys.argv[1:]
    
    run_all = len(flags) == 0
    do_crawl = "--crawl" in flags or "-c" in flags or run_all
    do_audit = "--audit" in flags or "-a" in flags or run_all
    do_pitch = "--pitch" in flags or "-p" in flags or run_all
    
    print("==================================================")
    print("      BILASPUR CRM MARKETING AGENT PIPELINE       ")
    print("==================================================")
    
    # 1. Initialize DB Tables
    init_db()
    
    # 2. Query OSM Overpass Leads
    if do_crawl:
        print("\n[Step 1/4] Running Lead Discovery (OSM Crawler)...")
        query_osm_leads()
        
    # 3. Analyze Digital Footprint / Websites
    if do_audit:
        print("\n[Step 2/4] Running Website Presence Audit...")
        audit_all_leads()
        
    # 4. Generate AI Pitches
    if do_pitch:
        print("\n[Step 3/4] Generating Personalized AI Pitches...")
        generate_all_pitches()
        
    # 5. Build HTML CRM Dashboard
    print("\n[Step 4/4] Compiling CRM Dashboard...")
    build_dashboard()
    
    print("\nPipeline execution completed successfully.")
    print("==================================================")

if __name__ == "__main__":
    main()
