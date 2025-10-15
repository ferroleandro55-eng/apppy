import streamlit as st
import os, json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")

def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

if st.session_state.get("usuario_logado") and st.session_state.usuario_logado.get("Admin"):
    st.header("Área do Admin — Gerenciamento de Usuários")
    usuarios = carregar_usuarios()

    # Cadastrar usuário
    st.subheader("➕ Cadastrar novo usuário")
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome completo")
        email_novo = st.text_input("E-mail do usuário")
        senha_nova = st.text_input("Senha", type="password")
        tipo_novo = st.selectbox("Tipo de usuário", ["Pais", "Admin / Mestre"])
        status_novo = st.selectbox("Status", ["Ativo", "Inativo"])
        sub_cadastrar = st.form_submit_button("Cadastrar usuário")
        if sub_cadastrar:
            e_norm = email_novo.strip().lower()
            if not nome or not email_novo or not senha_nova:
                st.warning("⚠️ Preencha todos os campos!")
            elif e_norm in usuarios:
                st.error("❌ Este e-mail já está cadastrado.")
            else:
                usuarios[e_norm] = {"Nome": nome.strip(), "Senha": senha_nova, "Tipo": tipo_novo, "Status": status_novo}
                salvar_usuarios(usuarios)
                st.success(f"✅ Usuário '{nome}' cadastrado!")

    # Remover usuário
    st.subheader("🗑 Remover usuário")
    if usuarios:
        options = [f"{u_email} — {u_data.get('Nome')}" for u_email, u_data in usuarios.items()]
        sel = st.selectbox("Escolha usuário", options)
        if st.button("Remover usuário"):
            email_sel = sel.split(" — ")[0]
            if email_sel in usuarios:
                nome_rem = usuarios[email_sel]["Nome"]
                del usuarios[email_sel]
                salvar_usuarios(usuarios)
                st.success(f"✅ Usuário '{nome_rem}' removido.")
            else:
                st.error("❌ Usuário não encontrado.")
    else:
        st.info("Nenhum usuário cadastrado.")
else:
    st.warning("❌ Você precisa estar logado como Admin para acessar esta página.")
