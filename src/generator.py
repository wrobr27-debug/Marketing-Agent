import sqlite3
from openai import OpenAI
from src.config import settings
from src.database import get_conn, update_lead_pitch

def generate_outreach_proposal(lead: dict) -> str:
    """Use the OpenCode LLM to draft a warm, highly personalized website development pitch."""
    if not settings.opencode_api_key:
        print("OpenCode API key not configured. Using fallback static pitch templates.")
        return get_fallback_pitch(lead)
        
    client = OpenAI(
        api_key=settings.opencode_api_key,
        base_url=settings.opencode_api_base
    )
    
    # Structure audit context
    audit_notes = lead.get("audit_notes") or ""
    website_url = lead.get("website_url") or ""
    has_website = lead.get("website_exists") == 1
    
    prompt_context = (
        f"Business Name: {lead.get('name')}\n"
        f"Industry/Category: {lead.get('category')}\n"
        f"Location/Address: {lead.get('address')}\n"
        f"Current Website status: {'Has website' if has_website else 'No website'}\n"
        f"Website URL: {website_url}\n"
        f"Audit Findings: {audit_notes}\n"
    )
    
    system_prompt = (
        "You are 'Developer Bilaspur', a helpful, expert local web developer from Bilaspur, Chhattisgarh. "
        "You write warm, respectful, and consultative sales outreach messages to local shopkeepers, merchants, schools, and clinic owners in Bilaspur. "
        "Your goal is to offer custom, high-speed, mobile-responsive web development services. "
        "Rules:\n"
        "1. Be extremely personalized. Mention the business name, location, and specific audit issues (e.g. no website, or slow site, or bad mobile layout).\n"
        "2. Keep the message short (under 120 words / 800 characters) so it fits in a WhatsApp or Instagram DM.\n"
        "3. Write in a friendly, conversational Hinglish (Hindi-English code-mixed) style, which reads natural and local to merchants in Chhattisgarh.\n"
        "4. Provide our website 'Developerbilaspur.in' and Instagram handle '@developerbilaspur' as references so they can check our work.\n"
        "5. DO NOT use generic placeholders like [Your Name] or [My Name]. Sign off directly as 'Developer Bilaspur' (website: Developerbilaspur.in, Instagram: @developerbilaspur)."
    )
    
    try:
        resp = client.chat.completions.create(
            model=settings.opencode_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Draft the outreach proposal for the following local business:\n\n{prompt_context}"}
            ],
            temperature=0.7,
            max_tokens=600
        )
        pitch = resp.choices[0].message.content
        return pitch.strip() if pitch else get_fallback_pitch(lead)
    except Exception as e:
        print(f"Failed to call OpenCode LLM for lead {lead.get('name')}: {e}")
        return get_fallback_pitch(lead)

def get_fallback_pitch(lead: dict) -> str:
    """Generate a clean static Hinglish pitch template in case LLM API fails."""
    name = lead.get("name")
    address = lead.get("address", "Bilaspur")
    has_website = lead.get("website_exists") == 1
    
    if not has_website:
        return (
            f"Namaste {name} Team! \n\n"
            f"Humne dekha ki aapki business {_extract_area(address)} me local logon ke beech kaafi popular hai. "
            f"Kya aapne kabhi business ke liye custom website banane ka socha hai? Ek custom mobile-friendly website se "
            f"Bilaspur ke aur bhi customers aapko Google par aasani se dhoondh sakenge. "
            f"Aap humare designs aur profile humari website 'Developerbilaspur.in' ya Instagram handle '@developerbilaspur' par check kar sakte hain. "
            f"Hum local developers hain aur aapke liye responsive website setup kar sakte hain. "
            f"Agar aap interested hain to please batayein!\n\n"
            f"Regards,\nDeveloper Bilaspur (Developerbilaspur.in / Insta: @developerbilaspur)"
        )
    else:
        return (
            f"Namaste {name} Team! \n\n"
            f"Humne aapki website ({lead.get('website_url')}) check ki. Aapka business {_extract_area(address)} me accha kar raha hai, "
            f"lekin aapki website mobile par slow load ho rahi hai aur responsive layout missing hai. "
            f"Hum aapke website ko optimize, fast, aur modern mobile-friendly design me update kar sakte hain. "
            f"Aap humare previous projects humari website 'Developerbilaspur.in' ya Instagram handle '@developerbilaspur' par check kar sakte hain. "
            f"Kya hum ispar discuss kar sakte hain?\n\n"
            f"Regards,\nDeveloper Bilaspur (Developerbilaspur.in / Insta: @developerbilaspur)"
        )

def _extract_area(address: str) -> str:
    if "Coordinates" in address:
        return "Bilaspur"
    parts = address.split(",")
    return parts[0].strip() if parts else "Bilaspur"

def generate_all_pitches():
    """Generate pitches for all leads that have been audited but not yet drafted."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    # Fetch leads that have been audited (website_exists is set) but status is still 'new'
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE website_exists IS NOT NULL AND status = 'new'")
    leads = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    print(f"Generating personalized pitches for {len(leads)} leads...")
    drafted_count = 0
    for lead in leads:
        print(f"  Drafting pitch for: {lead['name']}...")
        pitch = generate_outreach_proposal(lead)
        update_lead_pitch(lead['id'], pitch)
        drafted_count += 1
        
    print(f"Successfully generated pitches for {drafted_count} business leads.")
    return drafted_count

if __name__ == "__main__":
    generate_all_pitches()
