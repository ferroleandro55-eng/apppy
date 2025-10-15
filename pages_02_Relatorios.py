import streamlit as st
import os, json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

def carregar_rel_map():
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_rel_map(mapa):
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapa, f, indent=4, ensure_ascii=False)

def carregar_usuarios():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

usuarios = carregar_usuarios()
rel_map = carregar_rel_map()

if st.session_state.get("usuario_logado") and st.session_state.usuario_logado.get("Admin"):
    st.header("📁 Gerenciamento de Relatórios")
    # Upload
    with st.form("form_upload"):
        arquivo_pdf = st.file_uploader("Selecione o PDF", type=["pdf"])
        lista_pais = [u_data["Nome"] for u_data in usuarios.values() if u_data.get("Tipo","").lower()=="pais"]
        destino_sel = st.selectbox("Para qual usuário?", ["Todos"] + lista_pais)
        enviar = st.form_submit_button("Enviar PDF")
        if enviar:
            if not arquivo_pdf:
                st.warning("⚠️ Selecione um arquivo PDF antes de enviar.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = f"{timestamp}_{arquivo_pdf.name}"
                path = os.path.join(PASTA_RELATORIOS, safe_name)
                with open(path, "wb") as f:
                    f.write(arquivo_pdf.getbuffer())
                rel_map[safe_name] = destino_sel
                salvar_rel_map(rel_map)
                st.success(f"✅ PDF enviado para {destino_sel}")

    # Excluir
    st.subheader("🗑 Excluir relatórios")
    if rel_map:
        for fname, dono in list(rel_map.items()):
            path = os.path.join(PASTA_RELATORIOS, fname)
            if os.path.exists(path):
                col1, col2 = st.columns([5,1])
                col1.write(f"{fname} — {dono}")
                if col2.button("🗑", key=f"del_{fname}"):
                    os.remove(path)
                    del rel_map[fname]
                    salvar_rel_map(rel_map)
                    st.success(f"✅ Relatório '{fname}' excluído")
    else:
        st.info("Nenhum relatório enviado ainda.")
else:
    st.warning("❌ Você precisa estar logado como Admin para acessar esta página.")

