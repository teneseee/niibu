import csv
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

csv_file = 'deals.csv'

access_token = os.getenv('ACCES_TOKEN')
url_leads = "https://www.zohoapis.eu/crm/v2/Leads"
url_deals = "https://www.zohoapis.eu/crm/v2/Deals"

def send_batches(url, data, headers, label):
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        response = requests.post(url, json={"data": batch}, headers=headers)
        print(f'{label} batch {i//batch_size + 1} status: {response.status_code}')
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

leads = []
deals = []

with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        full_name = row['Person Name'].strip()
        if " " in full_name:
            parts = full_name.split()
            first_name = " ".join(parts[:-1])
            last_name = parts[-1]
        else:
            first_name = ""
            last_name = full_name or "Unknown"

        lead = {
            "First_Name": first_name,
            "Last_Name": last_name,
            "Email": row["Email"],
            "Phone": row["Phone"],
            "Lead_Source": row["Source"],
        }
        leads.append(lead)

        deal = {
            "Deal_Name": row['Deal Title'],
            "Amount": row["Budget"],
            "Stage": row["Status"].capitalize(), 
        }

        if row["Status"].lower() == "lost":
            deal["Description"] = row["Loss Reason"]

        deals.append(deal)


headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "Content-Type": "application/json"
}

send_batches(url_leads, leads, headers, "лиды")
send_batches(url_deals, deals, headers, "сделки")
