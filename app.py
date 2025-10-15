# app.py - versão completa e estável (com esqueci senha, excluir relatórios e direitos autorais)
import os
import json
import streamlit as st
from datetime import datetime

# --- Configuração ---
st.set_page_config(page_title="PortalPsico", page_icon="🧠", layout="wide")
st.markdown("<style>#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# --- Funções auxiliares ---
def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_usuarios(usuarios_dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios_dict, f, indent=4, ensure_ascii=False)

def carregar_rel_map():
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_rel_map(mapa):
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapa, f, indent=4, ensure_ascii=False)

def salvar_arquivo_para_usuario(usuario_nome, arquivo):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{arquivo.name}"
    destino = os.path.join(PASTA_RELATORIOS, safe_name)
    with open(destino, "wb") as f:
        f.write(arquivo.getbuffer())
    return safe_name

# --- Carregar dados ---
usuarios = carregar_usuarios()
rel_map = carregar_rel_map()

# --- Sessão ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "mostrar_recuperar" not in st.session_state:
    st.session_state.mostrar_recuperar = False

# --- Interface ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")

# LOGIN ou RECUPERAÇÃO
if not st.session_state.usuario_logado:
    if not st.session_state.mostrar_recuperar:
        col1, col2 = st.columns([2, 1])
        with col1:
            input_email = st.text_input("E-mail:")
            input_senha = st.text_input("Senha:", type="password")
            tipo_login = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"])
            entrar = st.button("Entrar")
            if st.button("Esqueci minha senha"):
                st.session_state.mostrar_recuperar = True
                st.experimental_rerun()
        with col2:
            st.info("Bem-vindo ao PortalPsico. Faça login ou recupere sua senha.")
    else:
        st.subheader("🔑 Recuperar senha")
        recuperar_email = st.text_input("Digite o e-mail cadastrado:")
        if st.button("Mostrar senha"):
            dados = usuarios.get(recuperar_email.strip().lower())
            if dados:
                st.success(f"✅ Sua senha é: **{dados['Senha']}**")
            else:
                st.error("❌ E-mail não encontrado.")
        if st.button("Voltar ao login"):
            st.session_state.mostrar_recuperar = False
            st.experimental_rerun()

# --- Lógica de login ---
if "usuario_logado" in st.session_state and not st.session_state.usuario_logado and not st.session_state.mostrar_recuperar:
    if "entrar" in locals() and entrar:
        email_norm = input_email.strip().lower()
        if tipo_login == "Admin / Mestre":
            if email_norm == "admin@portal.com" and input_senha == "12345":
                st.session_state.usuario_logado = {"Nome": "Admin Mestre", "Admin": True}
                st.success("Logado como Admin Mestre")
                st.experimental_rerun()
            else:
                st.error("❌ Credenciais de admin inválidas.")
        else:
            dados = usuarios.get(email_norm)
            if not dados:
                st.error("❌ E-mail não encontrado.")
            elif dados.get("Senha") != input_senha:
                st.error("❌ Senha incorreta.")
            elif dados.get("Status", "Ativo").lower() != "ativo":
                st.error("❌ Usuário inativo.")
            else:
                st.session_state.usuario_logado = {"Nome": dados["Nome"], "Email": email_norm, "Admin": False}
                st.success(f"✅ Bem-vindo(a), {dados['Nome']}!")
                st.experimental_rerun()

# --- ÁREA LOGADA ---
if st.session_state.usuario_logado:
    usuario = st.session_state.usuario_logado
    st.markdown("---")
    if usuario.get("Admin"):
        st.header("Área do Admin — Gerenciamento")

        # CADASTRAR USUÁRIO
        with st.expander("➕ Cadastrar novo usuário"):
            with st.form("form_cadastro", clear_on_submit=False):
                nome = st.text_input("Nome completo", key="cad_nome")
                email_novo = st.text_input("E-mail do usuário", key="cad_email")
                senha_nova = st.text_input("Senha", type="password", key="cad_senha")
                tipo_novo = st.selectbox("Tipo de usuário", ["Pais", "Admin / Mestre"], key="cad_tipo")
                status_novo = st.selectbox("Status", ["Ativo", "Inativo"], key="cad_status")
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
                        st.success(f"✅ Usuário '{nome}' cadastrado com sucesso!")

        # REMOVER USUÁRIO
        with st.expander("🗑 Remover usuário"):
            if usuarios:
                lista_usuarios = [f"{email} — {dados['Nome']}" for email, dados in usuarios.items()]
                sel = st.selectbox("Escolha um usuário", lista_usuarios)
                if st.button("Remover usuário selecionado"):
                    email_sel = sel.split(" — ")[0]
                    if email_sel in usuarios:
                        nome_rem = usuarios[email_sel]["Nome"]
                        del usuarios[email_sel]
                        salvar_usuarios(usuarios)
                        st.success(f"✅ Usuário '{nome_rem}' removido.")
                        st.experimental_rerun()
            else:
                st.info("Nenhum usuário cadastrado.")

        # UPLOAD DE RELATÓRIOS
        with st.expander("📁 Enviar relatórios"):
            with st.form("form_upload"):
                arquivo_pdf = st.file_uploader("Selecione o PDF", type=["pdf"])
                lista_pais = [u["Nome"] for u in usuarios.values() if u.get("Tipo", "").lower() == "pais"]
                destino_sel = st.selectbox("Enviar para", ["Todos"] + lista_pais)
                enviar = st.form_submit_button("Enviar")
                if enviar:
                    if not arquivo_pdf:
                        st.warning("⚠️ Selecione um arquivo primeiro.")
                    else:
                        saved_name = salvar_arquivo_para_usuario(destino_sel, arquivo_pdf)
                        rel_map[saved_name] = destino_sel
                        salvar_rel_map(rel_map)
                        st.success(f"✅ Relatório enviado para {destino_sel}!")

        # EXCLUIR RELATÓRIO
        with st.expander("🧹 Excluir relatórios"):
            if rel_map:
                relatorios = list(rel_map.keys())
                sel_rel = st.selectbox("Escolha o relatório para excluir", relatorios)
                if st.button("Excluir relatório"):
                    caminho = os.path.join(PASTA_RELATORIOS, sel_rel)
                    if os.path.exists(caminho):
                        os.remove(caminho)
                    del rel_map[sel_rel]
                    salvar_rel_map(rel_map)
                    st.success(f"🗑 Relatório '{sel_rel}' excluído com sucesso!")
                    st.experimental_rerun()
            else:
                st.info("Nenhum relatório para excluir.")

        # VISUALIZAR RELATÓRIOS
        st.subheader("📂 Relatórios Enviados")
        if rel_map:
            for fname, dono in rel_map.items():
                path = os.path.join(PASTA_RELATORIOS, fname)
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button(f"⬇️ {fname} ({dono})", f.read(), file_name=fname)
        else:
            st.info("Nenhum relatório disponível.")

    else:
        # ÁREA DO USUÁRIO (Pais)
        st.header("📜 Meus Relatórios")
        encontrados = [(f, os.path.join(PASTA_RELATORIOS, f)) for f, dono in rel_map.items() if dono == "Todos" or dono == usuario["Nome"]]
        if encontrados:
            for fname, path in encontrados:
                with open(path, "rb") as f:
                    st.download_button(f"⬇️ {fname}", f.read(), file_name=fname)
        else:
            st.warning("Nenhum relatório disponível.")

    # BOTÃO LOGOUT
    if st.button("Sair do sistema"):
        st.session_state.usuario_logado = None
        st.experimental_rerun()

# --- Rodapé com direitos autorais ---
st.markdown("""
<hr>
<div style='text-align:center; font-size:13px; color:gray;'>
© 2025 <b>PortalPsico</b> — Desenvolvido por <b>Leandro Ferro</b>. Todos os direitos reservados.
</div>
""", unsafe_allow_html=True)

























