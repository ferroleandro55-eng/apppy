# app.py - versão corrigida (salva e consulta e-mails normalized)
import os
import json
import streamlit as st
from datetime import datetime

# --- Configuração ---
st.set_page_config(page_title="Relatórios Psicopedagógicos", page_icon="🧠", layout="wide")
st.markdown("<style>#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# --- Helpers ---
def carregar_usuarios_normalizados():
    """Carrega usuarios.json e retorna dicionário com chaves em lower-case (email normalized)."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    normalized = {}
    for k, v in raw.items():
        key = k.strip().lower()
        # também normalize internamente o Tipo e Status (por segurança)
        v.setdefault("Nome", "")
        v.setdefault("Senha", "")
        v.setdefault("Tipo", "Pais")
        v.setdefault("Status", "Ativo")
        v["Tipo"] = v["Tipo"].strip()
        v["Status"] = v["Status"].strip()
        normalized[key] = v
    return normalized

def salvar_usuarios_normalizados(usuarios_dict):
    """Salva o dicionário (assume chaves já normalizadas)."""
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

# --- Carrega dados ---
usuarios = carregar_usuarios_normalizados()
rel_map = carregar_rel_map()

# --- Sessão (para logout) ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# --- UI Login ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")
col1, col2 = st.columns([2,1])
with col1:
    input_email = st.text_input("E-mail:")
    input_senha = st.text_input("Senha:", type="password")
    tipo_login = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"])
    entrar = st.button("Entrar")
with col2:
    if st.session_state.usuario_logado:
        st.write("Usuário:", st.session_state.usuario_logado.get("Nome"))
        if st.button("Logout"):
            st.session_state.usuario_logado = None
            st.experimental_rerun()

# --- Lógica de login ---
if entrar:
    email_norm = input_email.strip().lower()
    if tipo_login == "Admin / Mestre":
        if email_norm == "admin@portal.com" and input_senha == "12345":
            st.session_state.usuario_logado = {"Nome": "Admin Mestre", "Admin": True}
            st.success("Logado como Admin Mestre")
        else:
            st.error("❌ Credenciais de admin inválidas.")
    else:
        dados = usuarios.get(email_norm)
        if not dados:
            st.error("❌ E-mail não encontrado.")
        else:
            if dados.get("Senha") != input_senha:
                st.error("❌ Senha incorreta.")
            else:
                tipo = dados.get("Tipo", "Pais").strip().lower()
                status = dados.get("Status", "Ativo").strip().lower()
                if tipo != "pais":
                    st.error("❌ Este e-mail não é do tipo 'Pais'.")
                elif status != "ativo":
                    st.error("❌ Usuário não está ativo.")
                else:
                    st.session_state.usuario_logado = {"Nome": dados.get("Nome"), "Email": email_norm, "Admin": False}
                    st.success(f"✅ Bem-vindo(a), {dados.get('Nome')}!")

# --- Área logada ---
if st.session_state.usuario_logado:
    usuario = st.session_state.usuario_logado
    st.markdown("---")
    if usuario.get("Admin"):
        st.header("Área do Admin — Gerenciamento")
        # Cadastro (form)
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
                        salvar_usuarios_normalizados(usuarios)
                        st.success(f"✅ Usuário '{nome}' cadastrado! (email: {e_norm})")
                        # atualiza lista local
                        usuarios = carregar_usuarios_normalizados()

        # Remover (form)
        with st.expander("🗑 Remover usuário"):
            with st.form("form_remover"):
                if usuarios:
                    # mostrar emails com Nome para facilitar escolha
                    options = [f"{u_email} — {u_data.get('Nome')}" for u_email, u_data in usuarios.items()]
                    sel = st.selectbox("Escolha usuário (email — nome)", options, key="sel_remover")
                    remover = st.form_submit_button("Remover usuário")
                    if remover:
                        email_sel = sel.split(" — ")[0]
                        if email_sel in usuarios:
                            nome_rem = usuarios[email_sel]["Nome"]
                            del usuarios[email_sel]
                            salvar_usuarios_normalizados(usuarios)
                            st.success(f"✅ Usuário '{nome_rem}' removido.")
                        else:
                            st.error("❌ Usuário não encontrado.")
                else:
                    st.info("Nenhum usuário cadastrado.")

        # Upload de PDFs (form)
        with st.expander("📁 Upload de relatórios"):
            with st.form("form_upload"):
                arquivo_pdf = st.file_uploader("Selecione o PDF", type=["pdf"], key="upload_pdf")
                # lista nomes dos pais ativos
                lista_pais = [u_data["Nome"] for u_data in usuarios.values() if u_data.get("Tipo","").strip().lower()=="pais"]
                destino_sel = st.selectbox("Para qual usuário?", ["Todos"] + lista_pais, key="upload_dest")
                enviar = st.form_submit_button("Enviar PDF")
                if enviar:
                    if not arquivo_pdf:
                        st.warning("⚠️ Selecione um arquivo PDF antes de enviar.")
                    else:
                        saved_name = salvar_arquivo_para_usuario(destino_sel, arquivo_pdf)
                        # atualiza mapa
                        mapa = carregar_rel_map()
                        mapa[saved_name] = destino_sel
                        salvar_rel_map(mapa)
                        st.success(f"✅ PDF enviado para {destino_sel} como '{saved_name}'")

        # Ver todos relatórios
        st.subheader("Todos os relatórios (Admin)")
        mapa = carregar_rel_map()
        if mapa:
            for fname, dono in mapa.items():
                path = os.path.join(PASTA_RELATORIOS, fname)
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button(label=f"⬇️ {fname}  ({dono})", data=f.read(), file_name=fname, mime="application/pdf")
        else:
            st.info("Nenhum relatório enviado ainda.")

    else:
        # área do usuário (pais)
        st.header("Área do Usuário (Seus relatórios)")
        mapa = carregar_rel_map()
        achados = []
        for fname, dono in mapa.items():
            if dono == "Todos" or dono == usuario.get("Nome"):
                caminho = os.path.join(PASTA_RELATORIOS, fname)
                if os.path.exists(caminho):
                    achados.append((fname, caminho))
        if not achados:
            st.warning("Nenhum relatório disponível para você.")
        else:
            for fname, path in achados:
                with open(path, "rb") as f:
                    st.download_button(label=f"⬇️ {fname}", data=f.read(), file_name=fname, mime="application/pdf")


















