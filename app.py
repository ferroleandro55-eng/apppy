import os
import json
import streamlit as st
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# --- Configurações da página ---
st.set_page_config(page_title="🔐 RELATÓRIOS PSICOPEDAGÓGICOS", layout="wide")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Pastas e arquivos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USUARIOS_FILE = os.path.join(BASE_DIR, "usuarios.json")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# --- Carregar usuários ---
if os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "r") as f:
        usuarios = json.load(f)
else:
    usuarios = {}  # Estrutura: {email: {"nome": "", "senha": "", "tipo": "Pais"}}

# --- Função para salvar usuários ---
def salvar_usuarios():
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

# --- Função para enviar e-mail ---
def enviar_email(destino, assunto, corpo):
    try:
        email_remetente = "SEU_EMAIL_AQUI@gmail.com"
        senha_app = "SUA_SENHA_DE_APP_AQUI"
        msg = MIMEMultipart()
        msg["From"] = email_remetente
        msg["To"] = destino
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_remetente, senha_app)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.warning(f"⚠️ Não foi possível enviar e-mail: {e}")

# --- Login ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")
email_login = st.text_input("E-mail:")
senha_login = st.text_input("Senha:", type="password")
tipo_login = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"])
login_btn = st.button("Entrar")

usuario_logado = None

if login_btn:
    if tipo_login == "Admin / Mestre":
        if email_login == "admin@portal.com" and senha_login == "12345":
            usuario_logado = {"nome": "Admin", "tipo": "Admin"}
        else:
            st.error("❌ Credenciais de admin inválidas.")
    else:
        u = usuarios.get(email_login)
        if u and u["senha"] == senha_login and u["tipo"] == "Pais":
            usuario_logado = {"nome": u["nome"], "tipo": "Pais", "email": email_login}
        else:
            st.error("❌ E-mail ou senha incorretos.")

# --- Área logada ---
if usuario_logado:
    st.success(f"✅ Bem-vindo(a), {usuario_logado['nome']}!")

    # --- Área do ADM ---
    if usuario_logado["tipo"] == "Admin":
        st.subheader("👤 Gerenciamento de Usuários")
        with st.expander("Cadastrar novo usuário"):
            novo_nome = st.text_input("Nome completo", key="novo_nome")
            novo_email = st.text_input("E-mail", key="novo_email")
            novo_tipo = st.selectbox("Tipo", ["Pais"], key="novo_tipo")
            novo_senha = st.text_input("Senha", key="novo_senha")
            cadastrar_btn = st.button("Cadastrar")
            if cadastrar_btn:
                if novo_email in usuarios:
                    st.warning("Usuário já cadastrado.")
                elif novo_nome == "" or novo_email == "" or novo_senha == "":
                    st.warning("Preencha todos os campos.")
                else:
                    usuarios[novo_email] = {"nome": novo_nome, "senha": novo_senha, "tipo": novo_tipo}
                    salvar_usuarios()
                    enviar_email(novo_email, "Cadastro no Portal Psico", f"Sua conta foi criada!\nE-mail: {novo_email}\nSenha: {novo_senha}")
                    st.success(f"Usuário {novo_nome} cadastrado com sucesso e e-mail enviado!")

        st.subheader("📄 Relatórios")
        rel_files = [f for f in os.listdir(PASTA_RELATORIOS) if f.endswith(".pdf")]
        if rel_files:
            for pdf in rel_files:
                st.write(pdf)
                if st.button(f"Excluir {pdf}"):
                    os.remove(os.path.join(PASTA_RELATORIOS, pdf))
                    st.success(f"{pdf} removido!")
        else:
            st.info("Nenhum relatório enviado.")

        with st.expander("Enviar relatório"):
            arquivo_pdf = st.file_uploader("Selecionar PDF", type="pdf")
            email_para = st.selectbox("Para qual usuário?", ["Todos"] + [u["nome"] for u in usuarios.values() if u["tipo"] == "Pais"])
            enviar_rel = st.button("Enviar")
            if enviar_rel and arquivo_pdf:
                caminho = os.path.join(PASTA_RELATORIOS, arquivo_pdf.name)
                with open(caminho, "wb") as f:
                    f.write(arquivo_pdf.getbuffer())
                st.success("Relatório enviado!")
                st.info(f"Arquivo disponível para: {email_para}")

    # --- Área do USUÁRIO ---
    else:
        st.subheader("📄 Seus relatórios")
        arquivos_usuario = []
        for f in os.listdir(PASTA_RELATORIOS):
            for u_email, u_data in usuarios.items():
                if u_data["nome"] in f:
                    arquivos_usuario.append(f)
        if arquivos_usuario:
            for pdf in arquivos_usuario:
                caminho = os.path.join(PASTA_RELATORIOS, pdf)
                st.download_button(f"⬇️ {pdf}", data=open(caminho, "rb").read(), file_name=pdf, mime="application/pdf")
        else:
            st.info("Nenhum relatório disponível.")

    st.markdown("---")
    st.markdown("📝 Sistema criado por **leandro_ferro**. Todos os direitos reservados.")

# --- Recuperar senha ---
st.markdown("---")
st.subheader("🔑 Esqueci minha senha")
rec_email = st.text_input("Digite seu e-mail para recuperação", key="rec_email")
rec_btn = st.button("Recuperar senha")
if rec_btn:
    u = usuarios.get(rec_email)
    if u:
        enviar_email(rec_email, "Recuperação de senha", f"Sua senha é: {u['senha']}")
        st.success("✅ E-mail enviado com a sua senha!")
    else:
        st.error("❌ E-mail não encontrado.")
























