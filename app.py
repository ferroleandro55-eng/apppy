import os
import pandas as pd
import streamlit as st
from datetime import datetime

# --- Configuração da página ---
st.set_page_config(
    page_title="🔐 RELATÓRIOS PSICOPEDAGÓGICOS",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Esconder menu, barra lateral e rodapé ---
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Caminho base ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANILHA = os.path.join(BASE_DIR, "dados.xlsx")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")

if not os.path.exists(PASTA_RELATORIOS):
    os.makedirs(PASTA_RELATORIOS)

# --- Criar planilha se não existir ---
if not os.path.exists(PLANILHA):
    df = pd.DataFrame(columns=["Nome do Aluno", "E-mail", "Senha", "Status"])
    df.to_excel(PLANILHA, index=False)
else:
    df = pd.read_excel(PLANILHA, engine="openpyxl")

# --- Sessão ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'senha_recuperacao' not in st.session_state:
    st.session_state.senha_recuperacao = None

# --- Login ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")
email = st.text_input("E-mail:")
senha = st.text_input("Senha:", type="password")
tipo_login = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"])
login = st.button("Entrar")
recuperar_senha = st.button("Esqueci minha senha")

if recuperar_senha:
    if email:
        filtro = df[df["E-mail"].astype(str) == email]
        if not filtro.empty:
            st.info(f"Sua senha é: {filtro.iloc[0]['Senha']}")
        else:
            st.error("E-mail não encontrado.")
    else:
        st.warning("Digite o e-mail para recuperar a senha.")

if login:
    usuario = None
    if tipo_login == "Admin / Mestre":
        if email == "admin@portal.com" and senha == "12345":
            usuario = {"Nome do Aluno": "Admin Mestre", "Status": "Ativo", "Admin": True}
        else:
            st.error("❌ Credenciais de admin inválidas.")
    else:
        filtro = df[(df["E-mail"].astype(str) == email) & (df["Senha"].astype(str) == senha)]
        if not filtro.empty:
            usuario = filtro.iloc[0].to_dict()
            usuario["Admin"] = False
        else:
            st.error("❌ E-mail ou senha incorretos.")

    if usuario:
        st.session_state.usuario = usuario

# --- Área logada ---
if st.session_state.usuario:
    usuario = st.session_state.usuario
    st.success(f"✅ Bem-vindo(a), {usuario['Nome do Aluno']}!")
    st.info(f"📋 Status: {usuario['Status']}")

    if usuario.get("Admin"):
        st.subheader("📌 Área do Admin")
        # --- Cadastrar Usuário ---
        st.markdown("### Cadastrar novo usuário")
        with st.form("form_cadastro", clear_on_submit=True):
            nome_novo = st.text_input("Nome do Usuário")
            email_novo = st.text_input("E-mail")
            senha_nova = st.text_input("Senha")
            status_novo = st.selectbox("Status", ["Ativo", "Inativo"])
            tipo_novo = st.selectbox("Tipo de Login", ["Pais", "Admin / Mestre"])
            botao_cadastrar = st.form_submit_button("Cadastrar")
            if botao_cadastrar:
                if nome_novo and email_novo and senha_nova:
                    if email_novo in df["E-mail"].astype(str).values:
                        st.error("E-mail já cadastrado.")
                    else:
                        df.loc[len(df)] = [nome_novo, email_novo, senha_nova, status_novo]
                        df.to_excel(PLANILHA, index=False)
                        st.success(f"✅ Usuário {nome_novo} cadastrado com sucesso!")
                else:
                    st.warning("Preencha todos os campos.")

        # --- Remover usuário ---
        st.markdown("### Remover usuário")
        email_remover = st.selectbox("Selecione o usuário", df["E-mail"].astype(str))
        if st.button("Remover"):
            df = df[df["E-mail"].astype(str) != email_remover]
            df.to_excel(PLANILHA, index=False)
            st.success("Usuário removido com sucesso!")

        # --- Upload de Relatórios ---
        st.markdown("### Anexar Relatório PDF")
        relatorio_file = st.file_uploader("Escolha o PDF", type=["pdf"])
        if not df.empty:
            usuarios_para_relatorio = st.multiselect("Para quais usuários?", df["E-mail"].astype(str))
        else:
            usuarios_para_relatorio = []
        if st.button("Enviar Relatório"):
            if relatorio_file and usuarios_para_relatorio:
                for u in usuarios_para_relatorio:
                    caminho_pdf = os.path.join(PASTA_RELATORIOS, f"{u}_{relatorio_file.name}")
                    with open(caminho_pdf, "wb") as f:
                        f.write(relatorio_file.getbuffer())
                st.success("Relatório enviado!")
            else:
                st.warning("Selecione um arquivo e pelo menos um usuário.")

        # --- Remover Relatório ---
        st.markdown("### Excluir Relatório")
        pdfs_existentes = [f for f in os.listdir(PASTA_RELATORIOS) if f.lower().endswith(".pdf")]
        pdf_para_remover = st.selectbox("Selecione o relatório", pdfs_existentes)
        if st.button("Excluir Relatório"):
            if pdf_para_remover:
                os.remove(os.path.join(PASTA_RELATORIOS, pdf_para_remover))
                st.success("Relatório removido!")

    # --- Área do usuário ---
    else:
        st.subheader("📄 Seus relatórios:")
        nome_aluno = str(usuario["Nome do Aluno"])
        relatorios = [f for f in os.listdir(PASTA_RELATORIOS) if nome_aluno.lower() in f.lower() and f.lower().endswith(".pdf")]
        if not relatorios:
            st.warning("Nenhum relatório encontrado para você.")
        else:
            for pdf in relatorios:
                caminho_pdf = os.path.join(PASTA_RELATORIOS, pdf)
                st.download_button(
                    label=f"⬇️ Baixar {pdf}",
                    data=open(caminho_pdf, "rb").read(),
                    file_name=pdf,
                    mime="application/pdf"
                )
                st.info(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# --- Observação ---
st.markdown("---")
st.markdown("Sistema criado por **Leandro_Ferro** — Todos os direitos reservados.")




















