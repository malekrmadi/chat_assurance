# utils.py

import sqlite3
import re
import google.generativeai as genai
from prompts import sql_prompt, human_response_prompt_template

def generate_sql_query(history, question, max_history=5):
    full_prompt = "\n".join(sql_prompt + [f"Q: {q}\nA: {a}" for q, a in history[-max_history:]] + [f"Q: {question}"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(full_prompt)
    match = re.search(r"(SELECT.+?;)", response.text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

def execute_sql_query(sql_query, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return {"columns": columns, "rows": rows}, None
    except Exception as e:
        return None, str(e)

def generate_human_response(question, data):
    prompt = f"{human_response_prompt_template}\n\nQuestion: {question}\nData: {data}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
