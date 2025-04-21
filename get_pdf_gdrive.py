import io
import csv
import fitz
from openai import OpenAI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
from dotenv import load_dotenv

load_dotenv()


file_id = os.getenv('GD_FILE_ID')
credentials = "credentials.json"
openai_key = os.getenv('OPENAI_KEY')

client = OpenAI(api_key=openai_key)

def download_pdf(file_id):
    creds = service_account.Credentials.from_service_account_file(
        credentials,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def extract_from_pdf(file_stream):
    sources = []
    loss_reasons = []
    doc = fitz.open(stream=file_stream, filetype="pdf")
    for page in doc:
        text = page.get_text()
        for line in text.split("\n"):
            if "Источник:" in line:
                sources.append(line.split("Источник:")[-1].strip())
            if "Причина отказа:" in line:
                loss_reasons.append(line.split("Причина отказа:")[-1].strip())
    return sources, loss_reasons

pdf_file = download_pdf(file_id)
sources, reasons = extract_from_pdf(pdf_file)

prompt = f"""
У тебя есть два массива данных из CRM. Пожалуйста, проанализируй их и верни краткую таблицу в CSV-формате:
Вот данные из CRM:
Причины отказа: {reasons}
Источники лидов: {sources}

Верни **только** CSV — без описаний, заголовков, markdown, и пояснений. Пример желаемого результата:

Метрика,Значение
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

with open("pdf_analysis.csv", "w", encoding="utf-8") as f:
    f.write(csv_result)