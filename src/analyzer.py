import time
import httpx
from bs4 import BeautifulSoup
from src.database import get_conn, update_lead_audit

def audit_lead_website(url: str) -> dict:
    """Perform a lightweight performance and SEO audit of a website URL."""
    result = {
        "website_exists": True,
        "audit_speed": 0.0,
        "audit_notes": ""
    }
    
    if not url:
        result["website_exists"] = False
        result["audit_notes"] = "Lacks website listed. High priority candidate for new web presence development."
        return result
        
    # Ensure correct protocol prefix
    target_url = url.strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = "https://" + target_url
        
    start_time = time.time()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        resp = httpx.get(target_url, headers=headers, follow_redirects=True, timeout=12)
        duration = time.time() - start_time
        result["audit_speed"] = round(duration, 2)
        
        if resp.status_code != 200:
            result["audit_notes"] = f"Website returned non-ok status code {resp.status_code}. Site appears to be broken or offline."
            return result
            
        # Parse page DOM
        soup = BeautifulSoup(resp.text, "lxml")
        
        issues = []
        
        # Check mobile responsiveness
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            issues.append("Site lacks mobile viewport optimization tag (not responsive)")
            
        # Check SEO titles/descriptions
        title = soup.find("title")
        if not title or not title.text.strip():
            issues.append("Missing page title tag (bad for search visibility)")
            
        desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if not desc or not desc.get("content", "").strip():
            issues.append("Missing SEO meta description (bad click-through rate)")
            
        # Speed evaluation
        if duration > 3.5:
            issues.append(f"Slow load time: takes {duration:.2f} seconds to respond")
            
        if issues:
            result["audit_notes"] = f"Audit complete. Issues found: {'; '.join(issues)}."
        else:
            result["audit_notes"] = f"Website loads quickly ({duration:.2f}s) and passes basic SEO and mobile responsiveness checks."
            
    except Exception as e:
        duration = time.time() - start_time
        result["audit_speed"] = round(duration, 2)
        result["audit_notes"] = f"Failed to connect to website URL: {e} (site may be down)."
        
    return result

def audit_all_leads():
    """Audit all leads that haven't been audited yet."""
    conn = get_conn()
    cursor = conn.cursor()
    # Fetch leads where website_exists has not been evaluated yet
    cursor.execute("SELECT id, name, website_url FROM leads WHERE website_exists IS NULL")
    leads = cursor.fetchall()
    conn.close()
    
    print(f"Starting digital presence audit for {len(leads)} leads...")
    audited_count = 0
    for lead_id, name, url in leads:
        print(f"  Auditing: {name} ({url or 'No Website'})...")
        res = audit_lead_website(url)
        update_lead_audit(
            lead_id=lead_id,
            website_exists=res["website_exists"],
            audit_speed=res["audit_speed"],
            audit_notes=res["audit_notes"]
        )
        audited_count += 1
        
    print(f"Completed digital presence audits for {audited_count} business leads.")
    return audited_count

if __name__ == "__main__":
    audit_all_leads()
