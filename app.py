# app.py - Versão final estável
# Mantém dados locais em: usuarios.json, relatorios/, relatorios_map.json
# Autor: Leandro Ferro - PortalPsico

import os
import json
import streamlit as st
from datetime import datetime

# ----- Config -----
st.set_page_config(page_title="RELATÓRIOS PSICOPEDAGÓGICOS", page_icon="🧠", layout="wide")
st.markdown("<style>#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
REL_DIR = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
os.makedirs(REL_DIR, exist_ok=True)

# ----- Helpers -----
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

def normalize_email(e):
    return e.strip().lower()

def save_uploaded_pdf(file_obj):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{ts}_{file_obj.name}"
    path = os.path.join(REL_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(file_obj.getbuffer())
    return safe_name

# ----- Load storage -----
usuarios = load_json(DB_FILE, {})        # keys: email (normalized) -> { "Nome","Senha","Tipo","Status" }
rel_map = load_json(MAP_FILE, {})        # keys: filename -> owner ("Todos" or nome)

# ----- Session state init -----
if "user" not in st.session_state:
    st.session_state.user = None       # normalized email of logged user (or "admin@portal.com")
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ----- UI -----
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")
st.write("Acesso seguro — trabalho profissional")

# --- LOGIN FORM (usando st.form para evitar re-execução parcial) ---
with st.form("login_form"):
    login_email = st.text_input("E-mail", key="login_email")
    login_password = st.text_input("Senha", type="password", key="login_pwd")
    login_type = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"], key="login_type")
    submit_login = st.form_submit_button("Entrar")
    if submit_login:
        email_norm = normalize_email(login_email)
        if login_type == "Admin / Mestre":
            # fixed admin credentials
            if email_norm == "admin@portal.com" and login_password == "12345":
                st.session_state.user = "admin@portal.com"
                st.session_state.is_admin = True
                st.success("✅ Logado como Admin Mestre")
                st.experimental_rerun()
            else:
                st.error("❌ Credenciais de admin inválidas.")
        else:
            user = usuarios.get(email_norm)
            if not user:
                st.error("❌ E-mail não encontrado.")
            elif user.get("Senha") != login_password:
                st.error("❌ Senha incorreta.")
            elif user.get("Status","Ativo").strip().lower() != "ativo":
                st.error("❌ Usuário inativo.")
            else:
                st.session_state.user = email_norm
                st.session_state.is_admin = False
                st.success(f"✅ Bem-vindo(a), {user.get('Nome')}!")
                st.experimental_rerun()

# --- Link para recuperar senha (mostra área abaixo sem recarregar) ---
if st.button("Esqueci minha senha"):
    st.session_state.show_recover = True

if st.session_state.get("show_recover"):
    st.markdown("---")
    st.subheader("🔑 Recuperar senha")
    with st.form("recover_form"):
        rec_email = st.text_input("Digite o e-mail cadastrado", key="rec_email")
        rec_submit = st.form_submit_button("Mostrar senha")
        if rec_submit:
            em = normalize_email(rec_email)
            u = usuarios.get(em)
            if not u:
                st.error("❌ E-mail não encontrado.")
            else:
                # mostramos a senha diretamente (conforme pedido). Se quiser envio por e-mail futuramente, ativamos SMTP.
                st.success(f"✅ Sua senha é: **{u.get('Senha')}**")
    if st.button("Fechar recuperação"):
        st.session_state.show_recover = False
        st.experimental_rerun()

# --- If logged in show main area ---
if st.session_state.user:
    st.markdown("---")
    cols = st.columns([3,1])
    with cols[0]:
        if st.session_state.is_admin:
            st.header("Área do Admin — Gestão")
        else:
            st.header("Área do Usuário")
    with cols[1]:
        if st.button("Sair"):
            st.session_state.user = None
            st.session_state.is_admin = False
            st.experimental_rerun()

    # ---------- ADMIN ----------
    if st.session_state.is_admin:
        # CADASTRO (st.form to avoid reruns while typing)
        st.subheader("➕ Cadastrar novo usuário")
        with st.form("form_cadastro_admin"):
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
                    st.error("❌ Senha e confirmação não conferem.")
                elif em in usuarios:
                    st.error("❌ E-mail já cadastrado.")
                else:
                    usuarios[em] = {"Nome": cad_nome.strip(), "Senha": cad_senha, "Tipo": cad_tipo, "Status": cad_status}
                    save_json(DB_FILE, usuarios)
                    st.success(f"✅ Usuário '{cad_nome}' cadastrado.")
                    # don't log out admin; just refresh UI
                    st.experimental_rerun()

        st.markdown("---")
        # REMOVER USUÁRIO
        st.subheader("🗑 Remover usuário")
        if usuarios:
            opts = [f"{e} — {d.get('Nome')}" for e,d in usuarios.items()]
            with st.form("form_remover"):
                sel = st.selectbox("Escolha usuário (email — nome)", opts, key="rem_sel")
                rem_submit = st.form_submit_button("Remover")
                if rem_submit:
                    em_sel = sel.split(" — ")[0]
                    if em_sel in usuarios:
                        nome_rem = usuarios[em_sel]["Nome"]
                        del usuarios[em_sel]
                        save_json(DB_FILE, usuarios)
                        # also remove any rel_map entries for that user's Nome
                        to_delete = [k for k,v in rel_map.items() if v == usuarios.get(em_sel, {}).get("Nome")]
                        for k in to_delete:
                            rel_map.pop(k, None)
                            path = os.path.join(REL_DIR, k)
                            if os.path.exists(path):
                                try: os.remove(path)
                                except: pass
                        save_json(MAP_FILE, rel_map)
                        st.success(f"✅ Usuário '{nome_rem}' removido.")
                        st.experimental_rerun()
        else:
            st.info("Nenhum usuário cadastrado.")

        st.markdown("---")
        # UPLOAD
        st.subheader("📁 Enviar relatório (PDF)")
        with st.form("form_upload_admin"):
            upload_pdf = st.file_uploader("Selecione o PDF", type=["pdf"], key="up_pdf")
            # list of Names of Pais
            list_pais = [d["Nome"] for e,d in usuarios.items() if d.get("Tipo","").strip().lower() == "pais"]
            dest = st.selectbox("Enviar para", ["Todos"] + list_pais, key="up_dest")
            up_submit = st.form_submit_button("Enviar PDF")
            if up_submit:
                if not upload_pdf:
                    st.warning("⚠️ Selecione um PDF.")
                else:
                    saved = save_uploaded_pdf(upload_pdf)
                    rel_map[saved] = dest
                    save_json(MAP_FILE, rel_map)
                    st.success(f"✅ PDF enviado para '{dest}' como '{saved}'")
                    st.experimental_rerun()

        st.markdown("---")
        # LIST & DELETE RELS (admin)
        st.subheader("📂 Relatórios no servidor")
        if rel_map:
            for fname, owner in list(rel_map.items()):
                path = os.path.join(REL_DIR, fname)
                if os.path.exists(path):
                    cols = st.columns([8,1,1])
                    cols[0].write(f"{fname}  —  {owner}")
                    if cols[1].button("🗑 Excluir", key=f"del_{fname}"):
                        try:
                            os.remove(path)
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                        rel_map.pop(fname, None)
                        save_json(MAP_FILE, rel_map)
                        st.success(f"Arquivo '{fname}' excluído.")
                        st.experimental_rerun()
                    if cols[2].download_button("⬇️ Baixar", data=open(path,"rb").read(), file_name=fname, mime="application/pdf"):
                        pass
        else:
            st.info("Nenhum relatório enviado ainda.")

    # ---------- USER (Pais) ----------
    else:
        st.subheader("📄 Seus relatórios")
        # find all files where rel_map[f] == "Todos" or == user's Nome
        user_email = st.session_state.user
        user_nome = usuarios.get(user_email, {}).get("Nome")
        found = []
        for fname, owner in rel_map.items():
            if owner == "Todos" or owner == user_nome:
                path = os.path.join(REL_DIR, fname)
                if os.path.exists(path):
                    found.append((fname, path))
        if not found:
            st.warning("Nenhum relatório disponível para você.")
        else:
            for fname, path in sorted(found, reverse=True):
                with open(path, "rb") as f:
                    st.download_button(label=f"⬇️ {fname}", data=f.read(), file_name=fname, mime="application/pdf")

# ----- Footer -----
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:13px;'>© 2025 PortalPsico — Desenvolvido por <b>Leandro Ferro</b>. Todos os direitos reservados.</div>",
    unsafe_allow_html=True
)


























