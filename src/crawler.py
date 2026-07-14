import httpx
from src.database import add_lead

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bounding box coordinates for Bilaspur, Chhattisgarh to filter out other Bilaspurs
LAT_MIN, LAT_MAX = 21.8, 22.3
LON_MIN, LON_MAX = 81.9, 82.4

def query_osm_leads() -> int:
    """Query OpenStreetMap Overpass API for local businesses in Bilaspur, Chhattisgarh."""
    # Query shops, restaurants, cafes, schools, hospitals, and offices
    query = """
    [out:json][timeout:90];
    (
      node["shop"](21.8,81.9,22.3,82.4);
      way["shop"](21.8,81.9,22.3,82.4);
      node["amenity"="restaurant"](21.8,81.9,22.3,82.4);
      way["amenity"="restaurant"](21.8,81.9,22.3,82.4);
      node["amenity"="cafe"](21.8,81.9,22.3,82.4);
      way["amenity"="cafe"](21.8,81.9,22.3,82.4);
      node["amenity"="school"](21.8,81.9,22.3,82.4);
      way["amenity"="school"](21.8,81.9,22.3,82.4);
      node["amenity"="hospital"](21.8,81.9,22.3,82.4);
      way["amenity"="hospital"](21.8,81.9,22.3,82.4);
      node["office"](21.8,81.9,22.3,82.4);
      way["office"](21.8,81.9,22.3,82.4);
    );
    out center;
    """
    
    headers = {
        "User-Agent": "BilaspurMarketingCRM/1.0 (contact: wrobr27@gmail.com)"
    }
    
    print("Connecting to OpenStreetMap Overpass API...")
    try:
        resp = httpx.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=90)
        if resp.status_code != 200:
            print(f"Overpass API returned status code {resp.status_code}")
            return 0
            
        data = resp.json()
        elements = data.get("elements", [])
        print(f"Retrieved {len(elements)} raw elements from OSM.")
        
        added_count = 0
        for el in elements:
            tags = el.get("tags", {})
            
            # Extract basic info
            name = tags.get("name") or tags.get("brand") or tags.get("operator")
            if not name:
                continue
                
            # Filter location by coordinates to double-check bounds
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            if lat and lon:
                if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                    continue
            
            # Determine category
            category = "business"
            if "shop" in tags:
                category = f"shop:{tags['shop']}"
            elif "amenity" in tags:
                category = tags["amenity"]
            elif "office" in tags:
                category = f"office:{tags['office']}"
                
            # Phone details
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("mobile") or ""
            
            # Website details
            website = tags.get("website") or tags.get("contact:website") or tags.get("url") or ""
            
            # Construct address
            street = tags.get("addr:street") or ""
            housenumber = tags.get("addr:housenumber") or ""
            suburb = tags.get("addr:suburb") or ""
            city = tags.get("addr:city") or "Bilaspur"
            
            addr_parts = [p for p in [housenumber, street, suburb, city] if p]
            address = ", ".join(addr_parts) if addr_parts else f"Bilaspur, CG (Coordinates: {lat}, {lon})"
            
            # Write to SQLite DB
            success = add_lead(
                name=name,
                category=category,
                phone=phone,
                address=address,
                website_url=website
            )
            if success:
                added_count += 1
                
        print(f"Successfully processed and added {added_count} new leads to database.")
        return added_count
    except Exception as e:
        print(f"OSM Overpass query failed: {e}")
        return 0

if __name__ == "__main__":
    from src.database import init_db
    init_db()
    query_osm_leads()
