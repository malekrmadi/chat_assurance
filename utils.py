import os
import re
import psycopg2
import google.generativeai as genai
from prompts import sql_prompt, human_response_prompt_template

# Configurer le modèle Gemini utilisé
GEMINI_MODEL = "models/gemini-1.5-flash"

def generate_sql_query(history, question, max_history=5):
    """
    Génère une requête SQL depuis une question en anglais,
    en s'appuyant sur l’historique de conversation et Gemini 1.5 Flash.
    """
    full_prompt = "\n".join(
        sql_prompt +
        [f"Q: {q}\nA: {a}" for q, a in history[-max_history:] if a != "No SQL"] +
        [f"Q: {question}"]
    )
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(full_prompt)

    match = re.search(r"(SELECT.+?;)", response.text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None

    sql_query = match.group(1).strip()
    
    # Corriger les guillemets doubles inutiles, si jamais Gemini en produit
    sql_query = re.sub(r'""([^"]+)""', r'"\1"', sql_query)

    return sql_query

def execute_sql_query(sql_query):
    """
    Exécute une requête SQL sur PostgreSQL et retourne le résultat sous forme dict.
    Les informations de connexion sont lues depuis le fichier .env.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            dbname=os.getenv("PG_DB")
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return {"columns": columns, "rows": rows}, None
    except Exception as e:
        return None, str(e)

def generate_human_response(question, data):
    """
    Demande à Gemini 1.5 Flash de résumer les résultats SQL en langage naturel.
    """
    prompt = f"{human_response_prompt_template}\n\nQuestion: {question}\nData: {data}"
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text
