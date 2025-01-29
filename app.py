from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

NOTION_API_KEY = "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"
DATABASE_ID = "18a2b502752b8075af20fddfc4f99cbf"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# List of valid Notion status options
VALID_STATUSES = ["Interested", "Reviewing", "Offer Placed", "Accepted", "Rejected"]

def get_zillow_details(zillow_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(zillow_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        address = soup.find("h1", {"class": "ds-address-container"}).text.strip()
    except AttributeError:
        address = "Not Found"

    try:
        price = soup.find("span", {"class": "ds-value"}).text.strip()
    except AttributeError:
        price = "Not Available"

    return {"address": address, "price": price}

@app.route('/add', methods=['POST'])
def add_listing():
    data = request.json
    zillow_url = data.get("zillow_url")
    disclosure_link = data.get("disclosure_link", "")
    status = data.get("status", "Interested")  # Default to "Interested"

    # Ensure the provided status is valid
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status. Choose from: " + ", ".join(VALID_STATUSES)}), 400

    property_info = get_zillow_details(zillow_url)
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={property_info['address'].replace(' ', '+')}"

    notion_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Property Name": {"title": [{"text": {"content": property_info["address"]}}]},
            "Status": {"select": {"name": status}},  # Dynamically set status
            "Address": {"rich_text": [{"text": {"content": property_info["address"]}}]},
            "Asking Price ($$)": {"number": float(property_info["price"].replace("$", "").replace(",", "")) if property_info["price"] != "Not Available" else None},
            "Google Drive File": {"url": disclosure_link},
            "google map": {"url": google_maps_url}
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=notion_data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
