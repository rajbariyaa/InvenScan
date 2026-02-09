from io import StringIO
import app
import google.generativeai as genai
import pandas as pd
import psycopg2
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = f"""
Extract a table of items from this receipt. Include product, description, quantity, unit, price, and total.

Receipt:
{app.ocr_text}
"""
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content(prompt)

print("=== RAW GEMINI RESPONSE ===")
print(response.text)
print("===========================")

lines = response.text.strip().split("\n")
data = []

for line in lines:
    if set(line.strip()) <= {"|", "-", " "}:
        continue
    row = [cell.strip() for cell in line.strip().split("|") if cell.strip()]
    if len(row) == 6:
        data.append(row)

expected_columns = ["product", "description", "quantity", "unit", "price", "total"]
rows = data
if data:
    header = [cell.lower() for cell in data[0]]
    if header == expected_columns:
        rows = data[1:]

df = pd.DataFrame(rows, columns=expected_columns)

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432,
)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS invoice_items (
        id SERIAL PRIMARY KEY,
        product TEXT,
        description TEXT,
        quantity TEXT,
        unit TEXT,
        price TEXT,
        total TEXT
    );
    """
)
conn.commit()

insert_sql = (
    "INSERT INTO invoice_items (product, description, quantity, unit, price, total) "
    "VALUES (%s, %s, %s, %s, %s, %s)"
)
for row in df.itertuples(index=False):
    cursor.execute(insert_sql, tuple(row))

conn.commit()
cursor.close()
conn.close()
print("Data saved to database.")
