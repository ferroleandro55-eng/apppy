Importar OS
importar json
Importar Streamlit como st
de datetime importar datetime

# --- Configuração ---
st.set_page_config(page_title="PortalPsico", page_icon="🧠", layout="wide")
st.markdown("<estilo>#MainMenu{visibilidade:oculto;} rodapé {visibilidade: oculto;} cabeçalho {visibilidade: oculto;}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "usuarios.json")
PASTA_RELATORIOS = os.path.join(BASE_DIR, "relatorios")
MAP_FILE = os.path.join(BASE_DIR, "relatorios_map.json")
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

# --- Funções auxiliares ---
def carregar_usuarios():
se não for os.path.exists(DB_FILE):
retornar {}
com open(DB_FILE, "r", encoding="utf-8") como f:
retornar json.load(f)

def salvar_usuarios(usuarios_dict):
com open(DB_FILE, "w", encoding="utf-8") como f:
json.dump(usuarios_dict, f, recuo=4, ensure_ascii=Falso)

def carregar_rel_map():
Se os.path.exists(MAP_FILE):
com open(MAP_FILE, "r", encoding="utf-8") como f:
retornar json.load(f)
retornar {}

def salvar_rel_map(mapa):
com open(MAP_FILE, "w", encoding="utf-8") como f:
json.dump(mapa, f, recuo=4, ensure_ascii=Falso)

def salvar_arquivo_para_usuario(usuario_nome, arquivo):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{arquivo.name}"
    destino = os.path.join(PASTA_RELATORIOS, safe_name)
com open(destino, "wb") como f:
        f.write(arquivo.getbuffer())
Devolução safe_name

# --- Carregar dados ---
usuários = carregar_usuarios()
rel_map = carregar_rel_map()

# --- Sessão ---
se "usuario_logado" não estiver em st.session_state:
st.session_state.usuario_logado = Nenhum

se "mostrar_recuperar" não estiver em st.session_state:
st.session_state.mostrar_recuperar = Falso

# --- Interface ---
st.title("🔐 RELATÓRIOS PSICOPEDAGÓGICOS")

# LOGIN ou RECUPERAÇÃO
se não for st.session_state.usuario_logado:
se não st.session_state.mostrar_recuperar:
        col1, col2 = st.columns([2, 1])
com col1:
            input_email = st.text_input("E-mail:")
            input_senha = st.text_input("Senha:", type="password")
            tipo_login = st.selectbox("Entrar como", ["Pais", "Admin / Mestre"])
            entrar = st.button("Entrar")
            if st.button("Esqueci minha senha"):
st.session_state.mostrar_recuperar = Verdadeiro
                st.experimental_rerun()
com col2:
            st.info("Bem-vindo ao PortalPsico. Faça login ou recupere sua senha.")
mais:
        st.subheader("🔑 Recuperar senha")
        recuperar_email = st.text_input("Digite o e-mail cadastrado:")
        if st.button("Mostrar senha"):
dados = usuarios.get(recuperar_email.tira().lower())
se dados:
                st.success(f"✅ Sua senha é: **{dados['Senha']}**")
mais:
                st.error("❌ Este e-mail não está cadastrado.")
mais:
    # Área do Usuário (Pais)
    st.header("📜 Meus Relatórios")
    encontrados = [(f, os.path.join(PASTA_RELATORIOS, f)) for f, dono in rel_map.items() if dono == "Todos" or dono == st.session_state.usuario_logado["Nome"]]
se encontrados:
        for fname, path in encontrados:
com open(caminho, "rb") como f:
                st.download_button(f"⬇️ {fname}", f.read(), file_name=fname)
mais:
        st.warning("Nenhum relatório disponível.")

    # Cadastro de Usuário
com st.expander("📝 Cadastrar usuário"):
        nome = st.text_input("Nome do usuário:")
        senha_nova = st.text_input("Senha:", type="password")
        tipo_novo = st.selectbox("Tipo de usuário", ["Pais", "Admin / Mestre"])
        status_novo = st.selectbox("Status", ["Ativo", "Inativo"])
        e_norm = input_email.strip().lower()
        if st.button("Cadastrar"):
Se e_norm em Usuários:
                st.error("❌ Este e-mail já está cadastrado.")
mais:
                usuarios[e_norm] = {"Nome": nome.strip(), "Senha": senha_nova, "Tipo": tipo_novo, "Status": status_novo}
                salvar_usuarios(usuarios)
                st.session_state.usuario_logado = usuarios[e_norm]  # Atualiza a sessão para o novo usuário
                st.success(f"✅ Usuário '{nome}' cadastrado com sucesso!")

    # REMOVER USUÁRIO
    with st.expander("🗑 Remover usuário"):
Se usuarios:
            lista_usuarios = [f"{email} — {dados['Nome']}" for email, dados in usuarios.items()]
            sel = st.selectbox("Escolha um usuário", lista_usuarios)
            if st.button("Remover usuário selecionado"):
                email_sel = sel.split(" — ")[0]
Se email_sel em Usuários:
                    nome_rem = usuarios[email_sel]["Nome"]
                    del usuarios[email_sel]
                    salvar_usuarios(usuarios)
                    st.success(f"✅ Usuário '{nome_rem}' removido.")
                    st.experimental_rerun()
mais:
            st.info("Nenhum usuário cadastrado.")

    # UPLOAD DE RELATÓRIOS
    with st.expander("📁 Enviar relatórios"):
com st.form("form_upload"):
            arquivo_pdf = st.file_uploader("Selecione o PDF", type=["pdf"])
lista_pais = [u["Nome"] for u in usuarios.values() if you.get("Tipo", "").lower() == "pais"]
            destino_sel = st.selectbox("Enviar para", ["Todos"] + lista_pais)
            enviar = st.form_submit_button("Enviar")
Se enviar:
se não arquivo_pdf:
                    st.warning("⚠️ Selecione um arquivo primeiro.")
mais:
                    saved_name = salvar_arquivo_para_usuario(destino_sel, arquivo_pdf)
                    rel_map[saved_name] = destino_sel
                    salvar_rel_map(rel_map)
                    st.success(f"✅ Relatório enviado para {destino_sel}!")

    # EXCLUIR RELATÓRIO
    with st.expander("🧹 Excluir relatórios"):
Em caso rel_map:
relatórios = lista(rel_map.chaves())
sel_rel = st.selectbox("Escolha o relatório para excluir", relatórios)
            if st.button("Excluir relatório"):
                caminho = os.path.join(PASTA_RELATORIOS, sel_rel)
                if os.path.exists(caminho):
                    os.remove(caminho)
                del rel_map[sel_rel]
                salvar_rel_map(rel_map)
                st.success(f"🗑 Relatório '{sel_rel}' excluído com sucesso!")
                st.experimental_rerun()
mais:
            st.info("Nenhum relatório para excluir.")

    # VISUALIZAR RELATÓRIOS
    st.subheader("📂 Relatórios Enviados")
Em caso rel_map:
para fname, dono em rel_map.items():
caminho = os.path.join(PASTA_RELATORIOS, fname)
            st.write(f"- {fname} (enviado para: {dono})")
mais:
        st.info("Nenhum relatório enviado.")

    # BOTÃO LOGOUT
    if st.button("Sair do sistema"):
st.session_state.usuario_logado = Nenhum
        st.experimental_rerun()

# --- Rodapé com direitos autorais ---
st.markdown("""
< horas>
<div style='text-align:center; tamanho da fonte: 13px; cor: cinza;' >
© 2025 <b>PortalPsico</b> — Desenvolvido por <b>Leandro Ferro</b>. Todos os direitos reservados.
</div>
""", unsafe_allow_html=Verdadeiro)
```

























