import streamlit as st
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ========================================
# 🔐 CONFIGURAÇÕES GERAIS
# ========================================
st.set_page_config(page_title="Relatórios Psicopedagógicos", page_icon="🧠", layout="centered")

# Caminhos para arquivos de dados
USUARIOS_FILE = "usuarios.json"
RELATORIOS_DIR = "relatorios"

if not os.path.exists(RELATORIOS_DIR):
    os.makedirs(RELATORIOS_DIR)

# ========================================
# 📂 FUNÇÕES AUXILIARES
# ========================================
def carregar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

def enviar_email(destinatario, assunto, mensagem):
    try:
        remetente = "leandrobarbosa.barbosa123@gmail.com"  # e-mail do Leandro
        senha = "sgxzujfkhadrvezo"  # senha de app do Gmail (não senha real)
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(mensagem, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Erro ao enviar e-mail:", e)
        return False

def listar_relatorios(email_usuario):
    pasta_usuario = os.path.join(RELATORIOS_DIR, email_usuario)
    if not os.path.exists(pasta_usuario):
        return []
    return os.listdir(pasta_usuario)

# ========================================
# 🧾 TÍTULO E CABEÇALHO
# ========================================
st.markdown("<h1 style='text-align: center; color: #4B0082;'>🔐 RELATÓRIOS PSICOPEDAGÓGICOS</h1>", unsafe_allow_html=True)

# ========================================
# 🔑 LOGIN
# ========================================
usuarios = carregar_usuarios()

aba = st.sidebar.radio("Menu", ["Login", "Recuperar Senha", "Criar Usuário (ADM)"])

# ========================================
# 🔹 LOGIN DE USUÁRIO
# ========================================
if aba == "Login":
    email = st.text_input("E-mail:")
    senha = st.text_input("Senha:", type="password")
    tipo = st.selectbox("Entrar como", ["Pais", "Adm"])
    entrar = st.button("Entrar")

    if entrar:
        if email in usuarios and usuarios[email]["senha"] == senha and usuarios[email]["tipo"] == tipo:
            st.session_state["usuario"] = email
            st.session_state["tipo"] = tipo
            st.success(f"✅ Bem-vindo, {usuarios[email]['nome']}!")

        else:
            st.error("❌ E-mail ou senha incorreta.")

# ========================================
# 🔹 RECUPERAR SENHA
# ========================================
elif aba == "Recuperar Senha":
    st.subheader("🔄 Recuperar senha")
    recuperar_email = st.text_input("Digite seu e-mail cadastrado:")
    enviar = st.button("Enviar senha para o e-mail")

    if enviar:
        if recuperar_email in usuarios:
            senha_usuario = usuarios[recuperar_email]["senha"]
            mensagem = f"Sua senha de acesso ao sistema é: {senha_usuario}"
            enviado = enviar_email(recuperar_email, "Recuperação de Senha - Portal Psico", mensagem)
            if enviado:
                st.success("✅ Sua senha foi enviada para o e-mail informado!")
            else:
                st.error("❌ Falha ao enviar o e-mail. Verifique a conexão.")
        else:
            st.warning("⚠️ E-mail não encontrado no sistema.")

# ========================================
# 🔹 CADASTRO DE NOVOS USUÁRIOS (APENAS ADM)
# ========================================
elif aba == "Criar Usuário (ADM)":
    if "usuario" in st.session_state and st.session_state["tipo"] == "Adm":
        st.subheader("👥 Cadastrar novo usuário")
        with st.form("form_cadastro"):
            novo_nome = st.text_input("Nome completo do usuário")
            novo_email = st.text_input("E-mail do usuário")
            nova_senha = st.text_input("Senha", type="password")
            tipo_usuario = st.selectbox("Tipo de conta", ["Pais", "Adm"])
            cadastrar = st.form_submit_button("Cadastrar Usuário")

            if cadastrar:
                if novo_email in usuarios:
                    st.warning("⚠️ Este e-mail já está cadastrado.")
                elif not novo_nome or not novo_email or not nova_senha:
                    st.warning("⚠️ Preencha todos os campos.")
                else:
                    usuarios[novo_email] = {
                        "nome": novo_nome,
                        "senha": nova_senha,
                        "tipo": tipo_usuario
                    }
                    salvar_usuarios(usuarios)
                    st.success(f"✅ Usuário {novo_nome} cadastrado com sucesso!")
    else:
        st.error("❌ Apenas administradores podem cadastrar novos usuários.")

# ========================================
# 🧠 ÁREA LOGADA
# ========================================
if "usuario" in st.session_state:
    st.divider()
    email_logado = st.session_state["usuario"]
    tipo_logado = st.session_state["tipo"]

    st.markdown(f"👤 **Usuário logado:** {usuarios[email_logado]['nome']} ({tipo_logado})")

    # ===== Área do Administrador =====
    if tipo_logado == "Adm":
        st.subheader("📤 Upload de Relatórios")
        lista_usuarios = [u for u in usuarios.keys() if usuarios[u]["tipo"] == "Pais"]
        if lista_usuarios:
            destinatario = st.selectbox("Selecione o responsável (pai/mãe):", lista_usuarios)
            arquivo = st.file_uploader("Selecione o relatório (PDF)", type=["pdf"])
            if arquivo:
                pasta_usuario = os.path.join(RELATORIOS_DIR, destinatario)
                if not os.path.exists(pasta_usuario):
                    os.makedirs(pasta_usuario)
                caminho = os.path.join(pasta_usuario, arquivo.name)
                with open(caminho, "wb") as f:
                    f.write(arquivo.getbuffer())
                st.success(f"✅ Relatório '{arquivo.name}' enviado para {destinatario}.")

        st.subheader("🗑️ Excluir relatórios")
        usuario_alvo = st.selectbox("Selecione o usuário para excluir relatório:", lista_usuarios)
        relatorios_usuario = listar_relatorios(usuario_alvo)
        if relatorios_usuario:
            relatorio_excluir = st.selectbox("Selecione o relatório para excluir:", relatorios_usuario)
            if st.button("Excluir relatório"):
                os.remove(os.path.join(RELATORIOS_DIR, usuario_alvo, relatorio_excluir))
                st.success(f"🗑️ Relatório '{relatorio_excluir}' excluído com sucesso!")
        else:
            st.info("Nenhum relatório disponível para este usuário.")

    # ===== Área dos Pais =====
    else:
        st.subheader("📥 Meus Relatórios")
        relatorios = listar_relatorios(email_logado)
        if relatorios:
            for rel in relatorios:
                caminho = os.path.join(RELATORIOS_DIR, email_logado, rel)
                with open(caminho, "rb") as f:
                    st.download_button(label=f"📄 Baixar {rel}", data=f, file_name=rel)
        else:
            st.info("Ainda não há relatórios disponíveis para você.")

# ========================================
# ⚖️ DIREITOS AUTORAIS
# ========================================
st.markdown(
    "<hr><p style='text-align:center; color:gray;'>© 2025 Sistema desenvolvido por <b>Leandro Ferro</b>. Todos os direitos reservados.</p>",
    unsafe_allow_html=True
)
























