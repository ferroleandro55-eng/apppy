# app.py - Versão estável e corrigida (sem recarregar durante cadastro)
import os
import json
import streamlit as st
from datetime import datetime

# ---------------- Configurações ----------------
st.set_page_config(page_title="RELATÓRIOS PSICOPEDAGÓGICOS", page_icon="🧠", layout="wide")
st.markdown("<style>#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
REL_DIR = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
os.makedirs(REL_DIR, exist_ok=True)

# ---------------- Helpers ----------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_email(e: str) -> str:
    return e.strip().lower()

def save_uploaded_pdf(file_obj):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{ts}_{file_obj.name}"
    path = os.path.join(REL_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(file_obj.getbuffer())
    return safe_name

# ---------------- Load data ----------------
usuarios = load_json(DB_FILE, {})   # {email_norm: {"Nome","Senha","Tipo","Status"}}
rel_map = load_json(MAP_FILE, {})   # {filename: owner_name_or_Todos}

# ---------------- Session init ----------------
if "user" not in st.session_state:
    st.session_state.user = None        # normalized email of logged user
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_recover" not in st.session_state:
    st.session_state.show_recover = False
# safe place to hold transient messages:
if "msg" not in st.session_state:
    st.session_state.msg = None

# ---------------- UI: título ----------------
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")
st.write("Sistema local — usuários em arquivo JSON — relatórios em PDF na pasta `relatorios/`")

# ---------------- LOGIN (form) ----------------
if st.session_state.user is None and not st.session_state.show_recover:
    with st.form("login_form"):
        login_email = st.text_input("E-mail", key="login_email")
        login_password = st.text_input("Senha", type="password", key="login_pwd")
        login_type = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"], key="login_type")
        login_submit = st.form_submit_button("Entrar")
        if login_submit:
            em = normalize_email(login_email)
            if login_type == "Admin / Mestre":
                # credenciais fixas do Admin
                if em == "admin@portal.com" and login_password == "12345":
                    st.session_state.user = em
                    st.session_state.is_admin = True
                    st.session_state.msg = ("success", "✅ Logado como Admin Mestre")
                else:
                    st.session_state.msg = ("error", "❌ Credenciais de admin inválidas.")
            else:
                user = usuarios.get(em)
                if not user:
                    st.session_state.msg = ("error", "❌ E-mail não encontrado.")
                elif user.get("Senha") != login_password:
                    st.session_state.msg = ("error", "❌ Senha incorreta.")
                elif user.get("Status", "Ativo").strip().lower() != "ativo":
                    st.session_state.msg = ("error", "❌ Usuário inativo.")
                else:
                    st.session_state.user = em
                    st.session_state.is_admin = False
                    st.session_state.msg = ("success", f"✅ Bem-vindo(a), {user.get('Nome')}!")

    # botões fora do form para recuperar senha
    cols = st.columns([1,1,3])
    if cols[0].button("Esqueci minha senha"):
        st.session_state.show_recover = True
    if st.session_state.msg:
        typ, text = st.session_state.msg
        if typ == "success":
            st.success(text)
        else:
            st.error(text)

# ---------------- RECUPERAR SENHA ----------------
if st.session_state.show_recover:
    st.subheader("🔑 Recuperar senha")
    with st.form("recover_form"):
        rec_email = st.text_input("Digite o e-mail cadastrado para ver a senha", key="rec_email")
        rec_submit = st.form_submit_button("Mostrar senha")
        if rec_submit:
            em = normalize_email(rec_email)
            user = usuarios.get(em)
            if not user:
                st.error("❌ E-mail não encontrado.")
            else:
                st.success(f"✅ A senha cadastrada é: **{user.get('Senha')}**")
    if st.button("Voltar ao login"):
        st.session_state.show_recover = False
        st.session_state.msg = None

# ---------------- ÁREA LOGADA ----------------
if st.session_state.user:
    st.markdown("---")
    # cabeçalho com info e logout
    cols = st.columns([3,1])
    with cols[0]:
        if st.session_state.is_admin:
            st.header("Área do Admin — Gestão")
        else:
            nome_logado = usuarios.get(st.session_state.user, {}).get("Nome", st.session_state.user)
            st.header(f"Área do Usuário — {nome_logado}")
    with cols[1]:
        if st.button("Sair"):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.session_state.msg = None

    # ---------------- ADMIN ----------------
    if st.session_state.is_admin:
        # 1) Cadastrar novo usuário (form)
        st.subheader("➕ Cadastrar novo usuário")
        with st.form("form_cadastrar_admin"):
            cad_nome = st.text_input("Nome completo", key="cad_nome")
            cad_email = st.text_input("E-mail (ex: pai@email.com)", key="cad_email")
            cad_senha = st.text_input("Senha", type="password", key="cad_senha")
            cad_conf = st.text_input("Confirmar senha", type="password", key="cad_conf")
            cad_tipo = st.selectbox("Tipo de usuário", ["Pais", "Admin / Mestre"], key="cad_tipo")
            cad_status = st.selectbox("Status", ["Ativo", "Inativo"], key="cad_status")
            cad_submit = st.form_submit_button("Cadastrar")
            if cad_submit:
                em = normalize_email(cad_email)
                if not cad_nome or not cad_email or not cad_senha or not cad_conf:
                    st.warning("⚠️ Preencha todos os campos.")
                elif cad_senha != cad_conf:
                    st.error("❌ A senha e a confirmação não conferem.")
                elif em in usuarios:
                    st.error("❌ E-mail já cadastrado.")
                else:
                    usuarios[em] = {"Nome": cad_nome.strip(), "Senha": cad_senha, "Tipo": cad_tipo, "Status": cad_status}
                    save_json(DB_FILE, usuarios)
                    st.success(f"✅ Usuário '{cad_nome}' cadastrado com sucesso.")
                    # atualizar lista local (já salvo no arquivo)
        st.markdown("---")

        # 2) Remover usuário
        st.subheader("🗑 Remover usuário")
        if usuarios:
            opts = [f"{e} — {d.get('Nome')}" for e,d in usuarios.items()]
            with st.form("form_remover"):
                sel = st.selectbox("Escolha usuário (email — nome)", opts, key="rem_sel")
                rem_submit = st.form_submit_button("Remover")
                if rem_submit:
                    em_sel = sel.split(" — ")[0]
                    nome_rem = usuarios.get(em_sel, {}).get("Nome")
                    if em_sel in usuarios:
                        # remover entradas do mapa que apontam para esse nome
                        to_delete = [k for k,v in rel_map.items() if v == usuarios[em_sel].get("Nome")]
                        for k in to_delete:
                            # remove arquivo e map
                            path = os.path.join(REL_DIR, k)
                            if os.path.exists(path):
                                try: os.remove(path)
                                except: pass
                            rel_map.pop(k, None)
                        usuarios.pop(em_sel, None)
                        save_json(DB_FILE, usuarios)
                        save_json(MAP_FILE, rel_map)
                        st.success(f"✅ Usuário '{nome_rem}' removido.")
        else:
            st.info("Nenhum usuário cadastrado.")

        st.markdown("---")
        # 3) Upload de relatórios
        st.subheader("📁 Enviar relatório (PDF)")
        with st.form("form_upload_admin"):
            upload_pdf = st.file_uploader("Selecione o PDF", type=["pdf"], key="up_pdf")
            list_pais = [d["Nome"] for e,d in usuarios.items() if d.get("Tipo","").strip().lower() == "pais"]
            dest = st.selectbox("Enviar para", ["Todos"] + list_pais, key="up_dest")
            up_submit = st.form_submit_button("Enviar PDF")
            if up_submit:
                if not upload_pdf:
                    st.warning("⚠️ Selecione um PDF antes de enviar.")
                else:
                    saved = save_uploaded_pdf(upload_pdf)
                    rel_map[saved] = dest
                    save_json(MAP_FILE, rel_map)
                    st.success(f"✅ PDF enviado como '{saved}' para: {dest}")

        st.markdown("---")
        # 4) Listagem e exclusão de relatórios
        st.subheader("📂 Relatórios no servidor")
        if rel_map:
            # mostrar em ordem decrescente
            for fname, owner in sorted(rel_map.items(), reverse=True):
                path = os.path.join(REL_DIR, fname)
                if os.path.exists(path):
                    c0, c1, c2 = st.columns([6,1,1])
                    c0.write(f"{fname}  —  {owner}")
                    if c1.button("🗑 Excluir", key=f"del_{fname}"):
                        try:
                            os.remove(path)
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                        rel_map.pop(fname, None)
                        save_json(MAP_FILE, rel_map)
                        st.success(f"🗑 Relatório '{fname}' excluído.")
                    # botão de download
                    data = open(path, "rb").read()
                    c2.download_button("⬇️ Baixar", data=data, file_name=fname, mime="application/pdf")
        else:
            st.info("Nenhum relatório enviado ainda.")

    # ---------------- USUÁRIO (Pais) ----------------
    else:
        st.subheader("📄 Meus relatórios")
        user_email = st.session_state.user
        user_nome = usuarios.get(user_email, {}).get("Nome")
        encontrados = []
        for fname, owner in rel_map.items():
            if owner == "Todos" or owner == user_nome:
                path = os.path.join(REL_DIR, fname)
                if os.path.exists(path):
                    encontrados.append((fname, path))
        if not encontrados:
            st.warning("Nenhum relatório disponível para você.")
        else:
            for fname, path in sorted(encontrados, reverse=True):
                with open(path, "rb") as f:
                    st.download_button(label=f"⬇️ {fname}", data=f.read(), file_name=fname, mime="application/pdf")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("<div style='text-align:center; color:gray;'>© 2025 PortalPsico — Desenvolvido por <b>Leandro Ferro</b>. Todos os direitos reservados.</div>", unsafe_allow_html=True)





