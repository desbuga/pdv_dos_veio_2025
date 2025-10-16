# app_bunny_desbugaxuxu_v0_5_vendas.py
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="DesbugaXuxu v0.5 Vendas", layout="wide")

# Paths
DATA_DIR = "data"
CSV_STOCK = os.path.join(DATA_DIR, "estoque.csv")
CSV_USERS = os.path.join(DATA_DIR, "usuarios.csv")
TXT_FIN = os.path.join(DATA_DIR, "financeiro.txt")
CSV_SALES = os.path.join(DATA_DIR, "vendas.csv")

DEFAULT_COLUMNS = ["id", "item", "quantidade", "local", "preco_unit", "notas"]

# ---------- Aparência Office-like simples ----------
st.markdown("""
<style>
body, html, [class*="css"] {
    background-color: #ececec !important;
    color: #000000 !important;
    font-family: Arial, Helvetica, sans-serif !important;
}
section[data-testid="stSidebar"] {
    background-color: #d9d9d9 !important;
}
h1, h2, h3 {color:#000000 !important;}
.stButton>button {
    background-color: #c0c0c0;
    color:#000000;
    border:1px solid #808080;
}
.stButton>button:hover {
    background-color: #a0a0a0;
}
.stTextInput>div>input, textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Utilitários ----------
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def ensure_users_file():
    ensure_data_dir()
    if not os.path.exists(CSV_USERS):
        df = pd.DataFrame([
            ["admin", "1234", "admin", "Administrador"],
            ["xuxu", "1111", "colaborador", "Xuxu"]
        ], columns=["usuario", "senha", "role", "nome_exibicao"])
        df.to_csv(CSV_USERS, index=False)

def load_users_df():
    ensure_users_file()
    return pd.read_csv(CSV_USERS, dtype=str)

def authenticate(user, pwd):
    df = load_users_df()
    row = df[(df.usuario == user) & (df.senha == pwd)]
    if not row.empty:
        return row.iloc[0]["role"], row.iloc[0]["nome_exibicao"]
    return None, None

def load_stock_df():
    ensure_data_dir()
    if os.path.exists(CSV_STOCK):
        try:
            df = pd.read_csv(CSV_STOCK, dtype=str)
            for c in DEFAULT_COLUMNS:
                if c not in df.columns:
                    df[c] = ""
            df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0).astype(int)
            df["preco_unit"] = pd.to_numeric(df["preco_unit"], errors="coerce").fillna(0.0)
            return df[DEFAULT_COLUMNS]
        except Exception:
            return pd.DataFrame(columns=DEFAULT_COLUMNS)
    else:
        # arquivo inicial vazio
        return pd.DataFrame(columns=DEFAULT_COLUMNS)

def save_stock_df(df):
    ensure_data_dir()
    df.to_csv(CSV_STOCK, index=False)

def load_fin_text():
    ensure_data_dir()
    if os.path.exists(TXT_FIN):
        with open(TXT_FIN, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_fin_text(text):
    ensure_data_dir()
    with open(TXT_FIN, "w", encoding="utf-8") as f:
        f.write(text)

def load_sales_df():
    ensure_data_dir()
    if os.path.exists(CSV_SALES):
        try:
            s = pd.read_csv(CSV_SALES, dtype=str)
            # garantir colunas básicas
            for c in ["id","timestamp","item","quantidade","preco_unit","total","comprador","notas"]:
                if c not in s.columns:
                    s[c] = ""
            # normalizar tipos
            s["quantidade"] = pd.to_numeric(s["quantidade"], errors="coerce").fillna(0).astype(int)
            s["preco_unit"] = pd.to_numeric(s["preco_unit"], errors="coerce").fillna(0.0)
            s["total"] = pd.to_numeric(s["total"], errors="coerce").fillna(0.0)
            return s[["id","timestamp","item","quantidade","preco_unit","total","comprador","notas"]]
        except Exception:
            return pd.DataFrame(columns=["id","timestamp","item","quantidade","preco_unit","total","comprador","notas"])
    else:
        return pd.DataFrame(columns=["id","timestamp","item","quantidade","preco_unit","total","comprador","notas"])

def save_sales_df(df):
    ensure_data_dir()
    df.to_csv(CSV_SALES, index=False)

def next_id_for(df, idcol="id"):
    if df.empty:
        return 1
    vals = pd.to_numeric(df[idcol], errors="coerce")
    if vals.isna().all():
        return 1
    return int(vals.max()) + 1

def df_to_excel_bytes(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf.getvalue()

# ---------- Login ----------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("Login - DesbugaXuxu Vendas")
    c1, c2 = st.columns(2)
    user_input = c1.text_input("Usuário")
    pwd_input = c2.text_input("Senha", type="password")
    if st.button("Entrar"):
        role, name = authenticate(user_input, pwd_input)
        if role:
            st.session_state.user = {"usuario": user_input, "role": role, "nome": name}
            st.success("Acesso permitido.")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

usr = st.session_state.user
role = usr["role"]
name = usr["nome"]
st.sidebar.write("Usuário:", name)
st.sidebar.write("Função:", role)
if st.sidebar.button("Sair"):
    st.session_state.user = None
    st.rerun()

# ---------- Abas: Estoque | Vendas | Financeiro ----------
tabs = st.tabs(["Estoque", "Vendas", "Financeiro"])

# ---------- Aba Estoque ----------
with tabs[0]:
    st.header("Controle de Estoque")
    stock_df = load_stock_df()

    cA, cB, cC = st.columns(3)
    cA.metric("Itens totais", int(stock_df["quantidade"].sum()) if not stock_df.empty else 0)
    cB.metric("Valor total", f"R$ {(stock_df['quantidade'] * stock_df['preco_unit']).sum():,.2f}" if not stock_df.empty else "R$ 0,00")
    cC.metric("Atualização", datetime.now().strftime("%d/%m/%Y %H:%M"))

    if role == "admin":
        st.subheader("Tabela de Estoque (editável)")
        edited = st.data_editor(stock_df, num_rows="dynamic", use_container_width=True)
        if st.button("Salvar alterações no estoque"):
            save_stock_df(edited)
            st.success("Estoque salvo.")
    else:
        st.subheader("Tabela de Estoque")
        st.dataframe(stock_df, use_container_width=True)

    if role == "admin":
        st.subheader("Adicionar item")
        with st.form("add_stock", clear_on_submit=True):
            a1, a2, a3 = st.columns(3)
            item = a1.text_input("Item")
            qtd = a2.number_input("Quantidade", min_value=0, value=1, step=1)
            preco = a3.number_input("Preço unit. (R$)", min_value=0.0, value=0.0, step=0.5, format="%.2f")
            local = st.text_input("Local", value="estoque")
            notas = st.text_input("Notas")
            if st.form_submit_button("Adicionar ao estoque"):
                if not item.strip():
                    st.error("Preencha o campo Item.")
                else:
                    df = stock_df.copy()
                    new = {"id": next_id_for(df, "id"), "item": item, "quantidade": int(qtd),
                           "local": local, "preco_unit": float(preco), "notas": notas}
                    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                    save_stock_df(df)
                    st.success("Item adicionado ao estoque.")
                    stock_df = df  # atualiza local para sessão

    st.subheader("Exportar estoque")
    excel_bytes = df_to_excel_bytes(stock_df)
    st.download_button("Baixar estoque (Excel)", data=excel_bytes,
                       file_name=f"estoque_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Aba Vendas ----------
with tabs[1]:
    st.header("Registro de Vendas")
    stock_df = load_stock_df()  # recarrega pra ter a versão atual
    sales_df = load_sales_df()

    st.subheader("Registrar venda")
    # Monta select de itens disponíveis
    items_list = list(stock_df["item"].astype(str)) if not stock_df.empty else []
    if not items_list:
        st.info("Estoque vazio. Adicione itens antes de registrar vendas.")
    else:
        with st.form("sale_form", clear_on_submit=True):
            it = st.selectbox("Escolha o item", items_list)
            qty = st.number_input("Quantidade vendida", min_value=1, value=1, step=1)
            # buscar preco unitario atual do estoque
            row = stock_df[stock_df["item"] == it].iloc[0]
            default_price = float(row["preco_unit"]) if "preco_unit" in row and pd.notna(row["preco_unit"]) else 0.0
            price = st.number_input("Preço unit. (R$)", min_value=0.0, value=default_price, step=0.5, format="%.2f")
            buyer = st.text_input("Comprador (opcional)")
            notes = st.text_input("Notas")
            if st.form_submit_button("Registrar venda"):
                # ver disponibilidade
                idx = stock_df[stock_df["item"] == it].index[0]
                available = int(stock_df.at[idx, "quantidade"])
                if qty > available:
                    st.error(f"Estoque insuficiente. Disponível: {available}")
                else:
                    # atualizar estoque
                    stock_df.at[idx, "quantidade"] = available - int(qty)
                    save_stock_df(stock_df)
                    # registrar venda
                    new_sale = {
                        "id": next_id_for(sales_df, "id"),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "item": it,
                        "quantidade": int(qty),
                        "preco_unit": float(price),
                        "total": float(price) * int(qty),
                        "comprador": buyer,
                        "notas": notes
                    }
                    sales_df = pd.concat([sales_df, pd.DataFrame([new_sale])], ignore_index=True)
                    save_sales_df(sales_df)
                    st.success(f"Venda registrada: {qty} x {it} = R$ {new_sale['total']:,.2f}")

    st.markdown("---")
    st.subheader("Vendas registradas")
    sales_df = load_sales_df()
    if not sales_df.empty:
        st.dataframe(sales_df.sort_values("timestamp", ascending=False), use_container_width=True)
        # exportar vendas
        excel_vendas = df_to_excel_bytes(sales_df)
        st.download_button("Exportar vendas (Excel)", data=excel_vendas,
                           file_name=f"vendas_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write("Nenhuma venda registrada ainda.")

# ---------- Aba Financeiro ----------
with tabs[2]:
    st.header("Anotações Financeiras (bloco de notas)")
    ensure_data_dir()
    fin_text = load_fin_text()
    content = st.text_area("Bloco de Notas", value=fin_text, height=400)
    c1, c2 = st.columns(2)
    if c1.button("Salvar Anotações"):
        save_fin_text(content)
        st.success("Anotações salvas.")
    if c2.button("Carregar Anotações"):
        st.experimental_rerun()

    st.markdown("---")
    st.caption("v0.5 Vendas - Estoque + Vendas simples + Bloco financeiro. Layout simples e legível.")
