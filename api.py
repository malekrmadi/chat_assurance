from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
from utils import generate_sql_query, execute_sql_query, generate_human_response

# Charger les variables d'environnement (.env)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat_with_sql():
    data = request.get_json()

    if not data or "history" not in data or "question" not in data:
        return jsonify({"error": "Missing 'history' or 'question' in request body"}), 400

    history = data["history"]
    question = data["question"]

    if not isinstance(history, list):
        return jsonify({"error": "'history' must be a list"}), 400

    # Extraire uniquement les paires utilisateur/assistant pour Gemini
    chat_pairs = [
        (msg["content"], None) if msg["role"] == "user" else (None, msg["content"])
        for msg in history if msg.get("role") in ["user", "assistant"]
    ]

    # Nettoyer pour ne garder que les tuples (user, assistant)
    cleaned_history = []
    current_user = None
    for user_msg, assistant_msg in chat_pairs:
        if user_msg:
            current_user = user_msg
        elif assistant_msg and current_user:
            cleaned_history.append((current_user, assistant_msg))
            current_user = None

    # Générer la requête SQL en tenant compte du contexte
    sql_query = generate_sql_query(cleaned_history, question)

    if not sql_query:
        return jsonify({"response": "⚠️ Could not generate a valid SQL query."}), 200

    # Exécuter la requête SQL
    result, error = execute_sql_query(sql_query)

    if error:
        return jsonify({
            "sql": sql_query,
            "response": f"❌ Error executing SQL: {error}"
        }), 200

    # Résumer la réponse humaine
    human_response = generate_human_response(question, result["rows"])

    return jsonify({
        "sql": sql_query,
        "response": human_response,
        "columns": result["columns"],
        "rows": result["rows"]
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
