import streamlit as st
import os, json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")

def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

usuarios = carregar_usuarios()

st.header("🔑 Recuperação de senha")
email_rec = st.text_input("Digite seu e-mail")
if st.button("Recuperar senha"):
    email_norm = email_rec.strip().lower()
    dados = usuarios.get(email_norm)
    if dados:
        st.success(f"✅ Sua senha é: **{dados['Senha']}**")
    else:
        st.error("❌ E-mail não encontrado.")
