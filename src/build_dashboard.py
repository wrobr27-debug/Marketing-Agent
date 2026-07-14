import urllib.parse
from pathlib import Path
from datetime import datetime
from src.database import get_all_leads, init_db

DASHBOARD_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilaspur Business Leads CRM</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0a0e1a;
            --card-bg: rgba(20, 28, 48, 0.6);
            --border-glow: rgba(147, 51, 234, 0.3);
            --primary-purple: #9333ea;
            --primary-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --text-light: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background-color: var(--bg-deep);
            color: var(--text-light);
            min-height: 100vh;
            padding: 2.5rem 1.5rem;
            background-image: radial-gradient(circle at 10% 20%, rgba(147, 51, 234, 0.15) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 40%);
            background-attachment: fixed;
        }

        .container {
            max-width: 1300px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 1.5rem;
        }

        .logo-section h1 {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .logo-section p {
            color: var(--text-muted);
            font-size: 1rem;
            margin-top: 0.25rem;
        }

        .meta-info {
            text-align: right;
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1.25rem;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            border-color: var(--border-glow);
        }

        .stat-card .num {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-card .label {
            color: var(--text-muted);
            font-size: 0.9rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        /* Tabs Navigation */
        .tabs {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 2rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
        }

        .tab-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            white-space: nowrap;
        }

        .tab-btn.active, .tab-btn:hover {
            background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
            color: var(--text-light);
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(147, 51, 234, 0.4);
        }

        /* Leads Grid */
        .leads-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.75rem;
        }

        .lead-card {
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 1.5rem;
            padding: 1.75rem;
            backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .lead-card:hover {
            border-color: rgba(147, 51, 234, 0.4);
            box-shadow: 0 15px 35px rgba(147, 51, 234, 0.15);
            transform: scale(1.01);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .card-header h3 {
            font-size: 1.3rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.3;
        }

        .badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 50px;
            text-transform: uppercase;
        }

        .badge.cat {
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .badge.status {
            background: rgba(167, 139, 250, 0.15);
            color: #c084fc;
            border: 1px solid rgba(167, 139, 250, 0.3);
            margin-left: 0.5rem;
        }

        /* Lead Details */
        .detail-item {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
        }

        .detail-item strong {
            color: var(--text-light);
        }

        .detail-item a {
            color: var(--primary-blue);
            text-decoration: none;
        }

        .detail-item a:hover {
            text-decoration: underline;
        }

        /* Web Audit Block */
        .audit-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 1.25rem 0;
            border-left: 4px solid var(--primary-purple);
        }

        .audit-box.missing {
            border-left-color: var(--accent-red);
            background: rgba(239, 68, 68, 0.03);
        }

        .audit-box.success {
            border-left-color: var(--accent-green);
            background: rgba(16, 185, 129, 0.03);
        }

        .audit-title {
            font-size: 0.85rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.4rem;
            display: flex;
            justify-content: space-between;
        }

        .audit-notes {
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.4;
        }

        /* Pitch Box */
        .pitch-title {
            font-size: 0.85rem;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-light);
            margin-top: 1rem;
            margin-bottom: 0.4rem;
        }

        .pitch-box {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 0.75rem;
            padding: 1rem;
            font-size: 0.85rem;
            color: #cbd5e1;
            line-height: 1.5;
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
            margin-bottom: 1.25rem;
        }

        /* Card Actions */
        .card-actions {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
            margin-top: auto;
        }

        .action-btn {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: var(--text-light);
            padding: 0.6rem;
            border-radius: 0.5rem;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.25rem;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.1);
        }

        .action-btn.wa {
            background: rgba(16, 185, 129, 0.1);
            color: #34d399;
            border-color: rgba(16, 185, 129, 0.2);
        }

        .action-btn.wa:hover {
            background: rgba(16, 185, 129, 0.25);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        .action-btn.insta {
            background: rgba(239, 68, 68, 0.08);
            color: #f87171;
            border-color: rgba(239, 68, 68, 0.2);
        }

        .action-btn.insta:hover {
            background: rgba(239, 68, 68, 0.22);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        }

        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            background: var(--card-bg);
            border-radius: 1.5rem;
            border: 1px dashed rgba(255, 255, 255, 0.1);
        }

        .empty-state h3 {
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
        }

        .empty-state p {
            color: var(--text-muted);
        }

        /* Modal Alert */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-blue) 100%);
            color: #ffffff;
            padding: 1rem 2rem;
            border-radius: 50px;
            box-shadow: 0 10px 25px rgba(147, 51, 234, 0.4);
            font-weight: 600;
            display: none;
            z-index: 1000;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* Filter styling */
        .lead-card[data-status] {
            display: none;
        }

        .lead-card.active-status {
            display: flex;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-section">
                <h1>Bilaspur CRM Agent</h1>
                <p>Autonomous Lead Sourcing & Website Outreach Assistant</p>
            </div>
            <div class="meta-info">
                <p>Last Crawl: <span id="last-update">__LAST_UPDATE__</span></p>
                <p>Total Leads Discovered: <span id="total-count">__TOTAL_COUNT__</span></p>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="num" id="stat-discovered">__STAT_DISCOVERED__</div>
                <div class="label">Discovered</div>
            </div>
            <div class="stat-card">
                <div class="num" style="color: var(--accent-red);" id="stat-no-web">__STAT_NO_WEB__</div>
                <div class="label">Lacks Website</div>
            </div>
            <div class="stat-card">
                <div class="num" style="color: var(--primary-blue);" id="stat-has-web">__STAT_HAS_WEB__</div>
                <div class="label">Has Website</div>
            </div>
            <div class="stat-card">
                <div class="num" style="color: var(--accent-green);" id="stat-drafted">__STAT_DRAFTED__</div>
                <div class="label">Pitches Ready</div>
            </div>
        </div>

        <!-- Filter Tabs -->
        <div class="tabs">
            <button class="tab-btn active" onclick="filterStatus('all', this)">All Leads (__STAT_DISCOVERED__)</button>
            <button class="tab-btn" onclick="filterStatus('new', this)">New / Unaudited (__STAT_NEW__)</button>
            <button class="tab-btn" onclick="filterStatus('drafted', this)">Pitches Drafted (__STAT_DRAFTED__)</button>
            <button class="tab-btn" onclick="filterStatus('contacted', this)">Contacted (__STAT_CONTACTED__)</button>
            <button class="tab-btn" onclick="filterStatus('converted', this)">Converted (__STAT_CONVERTED__)</button>
            <button class="tab-btn" onclick="filterStatus('rejected', this)">Rejected (__STAT_REJECTED__)</button>
        </div>

        <!-- Leads Grid -->
        <div class="leads-grid" id="leads-container">
            __LEADS_CARDS__
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">Pitch copied to clipboard!</div>

    <script>
        function filterStatus(status, btn) {
            // Update active button styling
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter cards
            const cards = document.querySelectorAll('.lead-card');
            cards.forEach(c => {
                if (status === 'all') {
                    c.classList.add('active-status');
                } else if (c.getAttribute('data-status-val') === status) {
                    c.classList.add('active-status');
                } else {
                    c.classList.remove('active-status');
                }
            });
        }

        function copyPitch(id, text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast("Pitch proposal copied to clipboard!");
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.innerText = message;
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }

        // Initialize active-status class for all cards
        document.addEventListener('DOMContentLoaded', () => {
            const cards = document.querySelectorAll('.lead-card');
            cards.forEach(c => c.classList.add('active-status'));
        });
    </script>
</body>
</html>
"""

def _clean_phone(phone: str) -> str:
    """Standardize local Indian phone number to start with 91."""
    if not phone:
        return ""
    # Strip spaces, hyphens, brackets
    cleaned = "".join(c for c in phone if c.isdigit())
    if len(cleaned) == 10:
        return "91" + cleaned
    elif len(cleaned) == 12 and cleaned.startswith("91"):
        return cleaned
    return cleaned

def build_dashboard():
    """Build the static HTML dashboard compiling all leads into dist/index.html."""
    init_db()
    leads = get_all_leads()
    
    total_count = len(leads)
    no_web = sum(1 for l in leads if l.get("website_exists") == 0)
    has_web = sum(1 for l in leads if l.get("website_exists") == 1)
    
    status_counts = {"new": 0, "drafted": 0, "contacted": 0, "converted": 0, "rejected": 0}
    for l in leads:
        status_counts[l.get("status", "new")] = status_counts.get(l.get("status", "new"), 0) + 1
        
    lead_cards = []
    
    for l in leads:
        lead_id = l["id"]
        name = l["name"]
        cat = l["category"] or "business"
        address = l["address"] or "Bilaspur"
        phone = l["phone"] or ""
        website = l["website_url"] or ""
        exists = l["website_exists"]
        speed = l["audit_speed"] or 0.0
        notes = l["audit_notes"] or ""
        pitch = l["pitch_draft"] or ""
        status = l["status"] or "new"
        
        # Build audit HTML
        if exists == 0:
            audit_html = f"""<div class="audit-box missing">
                <div class="audit-title">Presence Check <span style="color: var(--accent-red);">❌ No Website</span></div>
                <div class="audit-notes">{notes}</div>
            </div>"""
        elif exists == 1:
            audit_html = f"""<div class="audit-box success">
                <div class="audit-title">Presence Check <span style="color: var(--accent-green);">✓ Has Website ({speed}s)</span></div>
                <div class="audit-notes">{notes}</div>
            </div>"""
        else:
            audit_html = """<div class="audit-box">
                <div class="audit-title">Presence Check <span>⏳ Pending Audit</span></div>
                <div class="audit-notes">Lead discovered. Audit will execute on next scheduler run.</div>
            </div>"""
            
        # Build pitch HTML
        if pitch:
            pitch_html = f"""<div class="pitch-title">Custom AI Pitch Draft</div>
            <div class="pitch-box" id="pitch-{lead_id}">{pitch}</div>"""
        else:
            pitch_html = """<div class="pitch-title">Custom AI Pitch Draft</div>
            <div class="pitch-box" style="color: var(--text-muted); font-style: italic;">Pitch draft will be generated on next AI scheduler run.</div>"""
            
        # Format WhatsApp link
        wa_phone = _clean_phone(phone)
        if wa_phone and pitch:
            encoded_pitch = urllib.parse.quote(pitch)
            wa_link = f"https://wa.me/{wa_phone}?text={encoded_pitch}"
        else:
            wa_link = "https://web.whatsapp.com"
            
        # Format Instagram / Google Search links
        clean_name = "".join(c for c in name if c.isalnum() or c.isspace()).strip()
        g_search_query = urllib.parse.quote(f"site:instagram.com {clean_name} Bilaspur")
        insta_link = f"https://www.google.com/search?q={g_search_query}"
        
        # Format telephone link
        tel_link = f"tel:{phone}" if phone else "#"
        
        # Format pitch text javascript escape
        js_pitch = pitch.replace("'", "\\'").replace("\\n", "\\\\n").replace("\n", "\\\\n")
        
        card = f"""
        <div class="lead-card" data-status-val="{status}">
            <div>
                <div class="card-header">
                    <h3>{name}</h3>
                    <div>
                        <span class="badge cat">{cat}</span>
                        <span class="badge status">{status}</span>
                    </div>
                </div>
                <div class="detail-item"><strong>Location:</strong> {address}</div>
                <div class="detail-item"><strong>Phone:</strong> {f'<a href="{tel_link}">{phone}</a>' if phone else '<span style="color: var(--accent-red);">Not listed</span>'}</div>
                <div class="detail-item"><strong>Website:</strong> {f'<a href="{website}" target="_blank">{website}</a>' if website else '<span style="color: var(--text-muted);">None</span>'}</div>
                {audit_html}
                {pitch_html}
            </div>
            <div class="card-actions">
                <button class="action-btn" onclick="copyPitch('{lead_id}', '{js_pitch}')">
                    <span>📋</span>
                    <span>Copy Pitch</span>
                </button>
                <a class="action-btn wa" href="{wa_link}" target="_blank">
                    <span>💬</span>
                    <span>WhatsApp</span>
                </a>
                <a class="action-btn insta" href="{insta_link}" target="_blank">
                    <span>📸</span>
                    <span>Instagram</span>
                </a>
            </div>
        </div>
        """
        lead_cards.append(card)
        
    # If no leads
    if not lead_cards:
        lead_cards.append("""
        <div class="empty-state">
            <h3>No Business Leads Found</h3>
            <p>Run the OSM Lead Discovery Crawler to query local businesses in Bilaspur.</p>
        </div>
        """)
        
    # Replace templates
    html = DASHBOARD_HTML_TEMPLATE
    html = html.replace("__LAST_UPDATE__", datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
    html = html.replace("__TOTAL_COUNT__", str(total_count))
    html = html.replace("__STAT_DISCOVERED__", str(total_count))
    html = html.replace("__STAT_NO_WEB__", str(no_web))
    html = html.replace("__STAT_HAS_WEB__", str(has_web))
    html = html.replace("__STAT_DRAFTED__", str(status_counts["drafted"]))
    html = html.replace("__STAT_NEW__", str(status_counts["new"]))
    html = html.replace("__STAT_CONTACTED__", str(status_counts["contacted"]))
    html = html.replace("__STAT_CONVERTED__", str(status_counts["converted"]))
    html = html.replace("__STAT_REJECTED__", str(status_counts["rejected"]))
    html = html.replace("__LEADS_CARDS__", "".join(lead_cards))
    
    # Save to dist/index.html
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    with open(dist_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"Static CRM dashboard compiled successfully in dist/index.html. Total Leads: {total_count}")

if __name__ == "__main__":
    build_dashboard()
