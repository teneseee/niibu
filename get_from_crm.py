import requests
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_KEY')
acces_token = os.getenv('ACCES_TOKEN')
client = OpenAI(api_key=api_key)

headers = {
    "Authorization": f"Zoho-oauthtoken {acces_token}"
}

def get_data(path):
    url = f"https://www.zohoapis.eu/crm/v2/{path}"
    all_crm_data = []
    page = 1

    while True:
        response = requests.get(f"{url}?page={page}", headers=headers)
        if response.status_code != 200:
            print(f"ошибка {path}, страница {page}:", response.text)
            break

        data = response.json()
        crm_data = data.get("data", [])
        all_crm_data.extend(crm_data)

        if not data.get("info", {}).get("more_records"):
            break
        page += 1
        time.sleep(0.5)

    return all_crm_data

leads = get_data("Leads")
deals = get_data("Deals")

print(f"Загружено сделок: {len(deals)}")
print(f"Загружено лидов: {len(leads)}")
print(type(leads))

deals_l_rsns = []
for deal in deals:
    if deal.get("Stage", "").lower() == "lost":
        reason = deal.get("Description", "Нет причины")
        deals_l_rsns.append(reason)

deals_budget = []
for deal in deals:
    amount = deal.get("Amount")
    deals_budget.append(amount)

leads_sources = []
for lead in leads:
    source = lead.get("Lead_Source")
    leads_sources.append(source)

short_reasons = deals_l_rsns[:100]
short_budgets = deals_budget[:100]
short_sources = leads_sources[:100]



prompt = f"""
У тебя есть три массива данных из CRM. Пожалуйста, проанализируй их и верни краткую таблицу в CSV-формате:
Вот данные из CRM:
Причины отказа: {short_reasons}
Бюджеты: {short_budgets}
Источники лидов: {short_sources}

Верни **только** CSV — без описаний, заголовков, markdown, и пояснений. Пример желаемого результата:

Метрика,Значение
Средний бюджет, 'значение'
Причина 1,'причина' 
Причина 2,'причина' 
...
Источник 1,'источник'
Источник 2,'источник'
...
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
)

csv_result = response.choices[0].message.content
print(csv_result)


with open("crm_analysis.csv", "w", encoding="utf-8") as f:
    f.write(csv_result)