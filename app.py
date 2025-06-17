# app.py

import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from utils import generate_sql_query, execute_sql_query, generate_human_response

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="SQL Chatbot", layout="centered")
st.title("🔍 SQL Query Chatbot with Gemini AI")

DB_PATH = "db.sqlite"

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_question = st.text_input("Ask your question about the database:", key="question_input")
submit = st.button("Send")

if submit and user_question:
    # Génération requête SQL
    sql_query = generate_sql_query(st.session_state["chat_history"], user_question)
    
    if sql_query:
        # Exécution requête SQL
        result, error = execute_sql_query(sql_query, DB_PATH)
        
        if error:
            bot_answer = f"❌ Error: {error}"
        else:
            # Résumé en langage naturel
            summary = generate_human_response(user_question, result["rows"])
            bot_answer = f"🧠 **SQL Query:** `{sql_query}`\n\n📊 **Result Summary:** {summary}"
    else:
        bot_answer = "⚠️ Could not generate a valid SQL query."

    # Ajouter à l'historique
    st.session_state["chat_history"].append((user_question, sql_query or "No SQL"))
    st.session_state["chat_history"].append(("Bot", bot_answer))

# Affichage du chat
st.write("---")
for speaker, msg in st.session_state["chat_history"]:
    if speaker == "Bot":
        st.markdown(f"> {msg}")
    else:
        st.markdown(f"**You:** {msg}")
