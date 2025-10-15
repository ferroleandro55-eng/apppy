import streamlit as st
from datetime import datetime
import os
import json

# --- Configuração da página ---
st.set_page_config(
    page_title="🔐 RELATÓRIOS PSICOPEDAGÓGICOS",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Esconde menus padrão do Streamlit ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- Diretórios e arquivos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USUARIOS_FILE = os.path.join(BASE_DIR, "usuarios.json")
RELATORIOS_DIR = os.path.join(BASE_DIR, "relatorios")

if not os.path.exists(RELATORIOS_DIR):
    os.makedirs(RELATORIOS_DIR)

# --- Criar arquivo de usuários se não existir ---
if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump({}, f)

with open(USUARIOS_FILE, "r") as f:
    usuarios = json.load(f)

# --- Interface de login ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")

email = st.text_input("E-mail:")
senha = st.text_input("Senha:", type="password")
tipo_login = st.selectbox("Entrar como:", ["Selecione", "Pais", "Admin / Mestre"])
login = st.button("Entrar")

usuario = None

# --- Lógica de login ---
if login:
    if tipo_login == "Admin / Mestre":
        if email.strip().lower() == "admin@portal.com" and senha == "12345":
            usuario = {"nome": "Admin Mestre", "email": email, "admin": True}
        else:
            st.error("❌ Credenciais de admin inválidas.")
    elif tipo_login == "Pais":
        if email in usuarios and usuarios[email]["senha"] == senha:
            usuario = usuarios[email]
            usuario["email"] = email
            usuario["admin"] = False
        else:
            st.error("❌ E-mail ou senha incorretos.")
    else:
        st.warning("⚠️ Selecione o tipo de login.")

# --- Função 'Esqueci minha senha' ---
with st.expander("🔑 Esqueci minha senha"):
    recuperar_email = st.text_input("Digite seu e-mail cadastrado:")
    if st.button("Recuperar senha"):
        if recuperar_email in usuarios:
            st.success(f"✅ Sua senha é: **{usuarios[recuperar_email]['senha']}**")
        elif recuperar_email.strip().lower() == "admin@portal.com":
            st.info("🧠 O admin usa a senha padrão: **12345**")
        else:
            st.error("❌ E-mail não encontrado.")

# --- Área logada ---
if usuario:
    st.success(f"✅ Bem-vindo(a), {usuario['nome']}!")

    # ------------------------ ÁREA DO ADMIN ------------------------
    if usuario["admin"]:
        st.subheader("📋 Painel do Administrador")

        # --- Cadastrar novo usuário ---
        st.markdown("---")
        st.subheader("👤 Cadastrar novo usuário")
        novo_nome = st.text_input("Nome completo:")
        novo_email = st.text_input("E-mail do usuário:")
        nova_senha = st.text_input("Senha:")
        if st.button("Cadastrar usuário"):
            if novo_email in usuarios:
                st.warning("⚠️ Esse e-mail já está cadastrado.")
            else:
                usuarios[novo_email] = {"nome": novo_nome, "senha": nova_senha}
                with open(USUARIOS_FILE, "w") as f:
                    json.dump(usuarios, f)
                st.success("✅ Usuário cadastrado com sucesso!")

        # --- Remover usuário ---
        st.markdown("---")
        st.subheader("🗑️ Remover usuário")
        if usuarios:
            email_remover = st.selectbox("Selecione o e-mail do usuário:", list(usuarios.keys()))
            if st.button("Remover usuário"):
                usuarios.pop(email_remover)
                with open(USUARIOS_FILE, "w") as f:
                    json.dump(usuarios, f)
                st.success("✅ Usuário removido com sucesso!")
        else:
            st.info("Nenhum usuário cadastrado ainda.")

        # --- Enviar relatório ---
        st.markdown("---")
        st.subheader("📎 Enviar relatório em PDF")
        arquivo = st.file_uploader("Selecione o arquivo PDF:", type=["pdf"])
        if usuarios:
            usuario_destino = st.selectbox("Enviar para o usuário:", list(usuarios.keys()))
        else:
            usuario_destino = None

        if st.button("Enviar PDF"):
            if not arquivo:
                st.warning("Selecione um arquivo antes de enviar.")
            elif not usuario_destino:
                st.warning("Selecione um usuário destino.")
            else:
                caminho = os.path.join(RELATORIOS_DIR, f"{usuario_destino}_{arquivo.name}")
                with open(caminho, "wb") as f:
                    f.write(arquivo.getbuffer())
                st.success("✅ Relatório enviado com sucesso!")

        # --- Excluir relatório ---
        st.markdown("---")
        st.subheader("🗑️ Excluir relatório existente")
        relatorios = [f for f in os.listdir(RELATORIOS_DIR) if f.endswith(".pdf")]
        if relatorios:
            relatorio_excluir = st.selectbox("Selecione o arquivo para excluir:", relatorios)
            if st.button("Excluir relatório"):
                os.remove(os.path.join(RELATORIOS_DIR, relatorio_excluir))
                st.success("✅ Relatório excluído com sucesso!")
        else:
            st.info("Nenhum relatório disponível para exclusão.")

        st.markdown("---")
        st.caption("📘 Sistema desenvolvido por **Leandro_Ferro** — Todos os direitos reservados ©")

    # ------------------------ ÁREA DO USUÁRIO ------------------------
    else:
        st.subheader("📂 Seus Relatórios")
        relatorios_user = [f for f in os.listdir(RELATORIOS_DIR) if f.startswith(usuario["email"])]
        if not relatorios_user:
            st.warning("⚠️ Nenhum relatório disponível no momento.")
        else:
            for relatorio in relatorios_user:
                caminho_pdf = os.path.join(RELATORIOS_DIR, relatorio)
                nome_pdf = relatorio.split("_", 1)[1]
                st.download_button(
                    label=f"⬇️ Baixar {nome_pdf}",
                    data=open(caminho_pdf, "rb").read(),
                    file_name=nome_pdf,
                    mime="application/pdf"
                )

        st.markdown("---")
        st.caption("📘 Sistema desenvolvido por **Leandro_Ferro** — Todos os direitos reservados ©")






















