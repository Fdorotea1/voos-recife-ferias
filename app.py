from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import time

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Voos Lisboa ↔ Recife | Férias escolares", page_icon="✈️", layout="wide")
HOJE = datetime.now(ZoneInfo("Europe/Lisbon")).date()
NIVEIS = ("Pré-escolar e 1.º ciclo", "5.º–8.º e 10.º anos", "9.º, 11.º e 12.º anos")
FONTE = "https://diariodarepublica.pt/dr/detalhe/despacho/8368-2024-873447631"
FONTE_2 = "https://diariodarepublica.pt/dr/detalhe/despacho/10430-2026-1160677001"
API_BASE = "https://partners.api.skyscanner.net/apiservices/v3/flights/live/search"


def ferias_escolares(nivel):
    dados = [
        ("Natal", "2026/2027", "2026-12-16", "2027-01-03", "2026-12-16", "2026-12-31", False),
        ("Carnaval", "2026/2027", "2027-02-06", "2027-02-10", "2027-02-08", "2027-02-10", False),
        ("Páscoa", "2026/2027", "2027-03-20", "2027-04-04", "2027-03-22", "2027-04-02", False),
        ("Natal", "2027/2028", "2027-12-18", "2028-01-02", "2027-12-20", "2027-12-31", False),
        ("Carnaval", "2027/2028", "2028-02-26", "2028-03-01", "2028-02-28", "2028-03-01", False),
        ("Páscoa", "2027/2028", "2028-04-01", "2028-04-17", "2028-04-03", "2028-04-17", False),
    ]
    fim_2027 = ["2027-06-30", "2027-06-11", "2027-06-04"][NIVEIS.index(nivel)]
    fim_2028 = ["2028-06-30", "2028-06-14", "2028-06-07"][NIVEIS.index(nivel)]
    data_27 = date.fromisoformat(fim_2027) + timedelta(days=1)
    data_28 = date.fromisoformat(fim_2028) + timedelta(days=1)
    dados.extend([
        ("Verão", "2026/2027", str(data_27), "2027-09-12", str(data_27), "2027-09-12", False),
        ("Verão", "2027/2028", str(data_28), "2028-08-31", str(data_28), "2028-08-31", True),
    ])
    return sorted([
        {"Nome": n, "Ano": a, "Início": date.fromisoformat(i), "Fim": date.fromisoformat(f),
         "Oficial início": date.fromisoformat(oi), "Oficial fim": date.fromisoformat(of),
         "Provisório": pr, "Férias": n + " · " + a}
        for n, a, i, f, oi, of, pr in dados
    ], key=lambda x: x["Início"])


def procurar_combinacoes(periodos, inicio_min, dur_min, dur_max, margem):
    linhas = []
    for p in periodos:
        partida = max(p["Início"], inicio_min, HOJE + timedelta(days=1))
        limite = p["Fim"] - timedelta(days=dur_min + margem)
        while partida <= limite:
            for dur in range(dur_min, dur_max + 1):
                regresso = partida + timedelta(days=dur)
                if regresso + timedelta(days=margem) > p["Fim"]:
                    continue
                score = int(partida.weekday() in (1, 2, 3)) + int(regresso.weekday() in (1, 2, 3))
                linhas.append({
                    "Férias": p["Férias"], "Ida": partida, "Volta": regresso,
                    "Dias": dur, "Dia ida": partida.strftime("%a"), "Dia volta": regresso.strftime("%a"),
                    "Prioridade": score, "Provisório": p["Provisório"],
                })
            partida += timedelta(days=1)
    return linhas


def link_skyscanner(ida, volta, idade, diretos):
    parametros = {
        "origin": "LIS", "destination": "REC", "outboundDate": ida.isoformat(),
        "inboundDate": volta.isoformat(), "adultsv2": 3, "childrenv2": str(idade),
        "cabinclass": "economy", "preferDirects": str(diretos).lower(),
        "market": "PT", "locale": "pt-PT", "currency": "EUR", "sortby": "cheapest",
    }
    return "https://www.skyscanner.net/flights/day-view?" + urlencode(parametros)


def converter_preco(v):
    if pd.isna(v):
        return None
    texto = str(v).replace("€", "").strip().replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        val = float(Decimal(texto))
        return val if val >= 0 else None
    except (InvalidOperation, ValueError):
        return None


def importar_orcamentos(ficheiro, diretos):
    try:
        t = pd.read_csv(ficheiro, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    except Exception as ex:
        raise ValueError("Não foi possível ler o CSV.") from ex
    t.columns = t.columns.str.strip().str.lower()
    if not {"ida", "volta", "companhia", "tipo"}.issubset(t.columns):
        raise ValueError("O CSV requer as colunas ida, volta, companhia e tipo.")
    if "preco_total_eur" not in t.columns and not {"preco_adulto_eur", "preco_crianca_eur"}.issubset(t.columns):
        raise ValueError("Indica preco_total_eur ou os preços individuais do adulto e da criança.")
    t["ida"] = pd.to_datetime(t["ida"], format="%Y-%m-%d", errors="coerce").dt.date
    t["volta"] = pd.to_datetime(t["volta"], format="%Y-%m-%d", errors="coerce").dt.date
    t = t.dropna(subset=["ida", "volta"])
    t = t[t["volta"] > t["ida"]].copy()
    if diretos:
        t = t[t["tipo"].fillna("").str.strip().str.lower().isin(
            ["direto", "directo", "direct", "nonstop", "sem escalas"])].copy()
    t["total_eur"] = t["preco_total_eur"].map(converter_preco) if "preco_total_eur" in t else float("nan")
    if {"preco_adulto_eur", "preco_crianca_eur"}.issubset(t.columns):
        calculado = 3 * t["preco_adulto_eur"].map(converter_preco) + t["preco_crianca_eur"].map(converter_preco)
        t["total_eur"] = t["total_eur"].fillna(calculado)
    return t.dropna(subset=["total_eur"]).sort_values("total_eur")


def _converter_moeda(preco):
    div = {"PRICE_UNIT_WHOLE": 1, "PRICE_UNIT_CENTI": 100,
           "PRICE_UNIT_MILLI": 1000, "PRICE_UNIT_MICRO": 1000000}
    try:
        return float(Decimal(str(preco["amount"])) / div[preco["unit"]])
    except (KeyError, InvalidOperation, TypeError):
        return None


def extrair_ofertas(dados, diretos):
    res = dados.get("content", {}).get("results", {})
    legs, segs, carriers = (res.get("legs", {}), res.get("segments", {}), res.get("carriers", {}))
    ofertas = []
    for itinerario in res.get("itineraries", {}).values():
        partes = [legs.get(k, {}) for k in itinerario.get("legIds", [])]
        if len(partes) != 2:
            continue
        segmentos = [p.get("segmentIds", []) for p in partes]
        if diretos and any(len(s) != 1 for s in segmentos):
            continue
        nomes = set()
        for refs in segmentos:
            for segid in refs:
                seg = segs.get(segid, {})
                cid = seg.get("marketingCarrierId") or seg.get("operatingCarrierId")
                if cid:
                    nomes.add(carriers.get(cid, {}).get("name", cid))
        for p in itinerario.get("pricingOptions", []):
            preco = _converter_moeda(p.get("price", {}))
            if preco is None:
                continue
            links = [x.get("deepLink") for x in p.get("items", []) if x.get("deepLink")]
            ofertas.append({
                "Companhia": ", ".join(sorted(nomes)) or "Consultar operador",
                "Escalas (total)": sum(max(len(s) - 1, 0) for s in segmentos),
                "Família (€)": preco, "Reservar": links[0] if len(links) == 1 else "",
                "Reservas separadas": len(links) > 1,
            })
    return sorted(ofertas, key=lambda a: a["Família (€)"])


def procurar_api(chave, ida, volta, idade, diretos):
    def leg(orig, destino, dia):
        return {"originPlaceId": {"iata": orig}, "destinationPlaceId": {"iata": destino},
                "date": {"year": dia.year, "month": dia.month, "day": dia.day}}
    payload = {"query": {"market": "PT", "locale": "pt-PT", "currency": "EUR", "adults": 3,
                         "childrenAges": [idade], "cabinClass": "CABIN_CLASS_ECONOMY",
                         "queryLegs": [leg("LIS", "REC", ida), leg("REC", "LIS", volta)]}}
    cab = {"x-api-key": chave, "Content-Type": "application/json"}
    try:
        r = requests.post(API_BASE + "/create", json=payload, headers=cab, timeout=25)
        r.raise_for_status()
        d = r.json()
        ofertas = extrair_ofertas(d, diretos)
        completas = d.get("status") == "RESULT_STATUS_COMPLETE"
        sessao = d.get("sessionToken")
        for _ in range(3):
            if completas or not sessao:
                break
            time.sleep(1.5)
            r = requests.post(API_BASE + "/poll/" + sessao, headers=cab, timeout=25)
            r.raise_for_status()
            d = r.json()
            novas = extrair_ofertas(d, diretos)
            if d.get("action") == "RESULT_ACTION_REPLACED":
                ofertas = novas
            else:
                chaves = {(x["Família (€)"], x["Reservar"]) for x in ofertas}
                ofertas.extend(x for x in novas if (x["Família (€)"], x["Reservar"]) not in chaves)
            completas = d.get("status") == "RESULT_STATUS_COMPLETE"
        return sorted(ofertas, key=lambda x: x["Família (€)"]), completas
    except requests.RequestException as ex:
        raise RuntimeError("Erro ao consultar a API Skyscanner. Confirma credenciais e permissões de parceiro.") from ex


st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 1.7rem;}
.hero {padding:1.5rem 1.7rem;background:linear-gradient(110deg,#093948,#087c8f);
border-radius:18px;color:white;margin-bottom:1.1rem}
.hero h1 {color:white;margin:0;font-size:2rem}
.hero p {margin:.55rem 0 0;color:#e6f5f7}
</style>
<div class="hero"><h1>✈️ Lisboa ↔ Recife</h1>
<p>Pesquisa inteligente nas férias escolares · 3 adultos + 1 criança · ida e volta</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configurar pesquisa")
    modo = st.radio("Tipo de pesquisa", ["Férias escolares", "Datas livres"])
    idade = st.number_input("Idade da criança", min_value=2, max_value=17, value=7, step=1)
    diretos = st.checkbox("Apenas voos diretos", value=False)
    dur_min, dur_max = st.slider("Dias entre ida e volta", 3, 30, (6, 10))
    if modo == "Férias escolares":
        nivel = st.selectbox("Ciclo/ano escolar", NIVEIS)
        nomes = st.multiselect("Pausas escolares", ["Natal", "Carnaval", "Páscoa", "Verão"],
                               default=["Natal", "Carnaval", "Páscoa", "Verão"])
        margem = st.slider("Dias de margem para regressar a Lisboa", 0, 2, 1,
                           help="A chegada do Recife pode ocorrer no dia seguinte.")
        desde = st.date_input("Partidas a partir de", value=HOJE, min_value=HOJE, max_value=date(2028, 8, 31),
                              format="DD/MM/YYYY")
        periodos = [p for p in ferias_escolares(nivel) if p["Nome"] in nomes and p["Fim"] >= desde]
        linhas = procurar_combinacoes(periodos, desde, dur_min, dur_max, margem)
    else:
        inicio = st.date_input("Partidas a partir de", value=HOJE + timedelta(days=30),
                               min_value=HOJE, format="DD/MM/YYYY")
        fim = st.date_input("Regresso até", value=inicio + timedelta(days=30), min_value=inicio,
                            format="DD/MM/YYYY")
        if (fim - inicio).days > 120:
            st.warning("Intervalo limitado a 120 dias.")
            fim = inicio + timedelta(days=120)
        periodos = [{"Nome": "Datas livres", "Ano": "personalizado", "Férias": "Datas livres",
                     "Início": inicio, "Fim": fim, "Provisório": False,
                     "Oficial início": inicio, "Oficial fim": fim}]
        linhas = procurar_combinacoes(periodos, inicio, dur_min, dur_max, 0)

df = pd.DataFrame(linhas)
st.caption("Sem preços inventados: esta aplicação apresenta datas possíveis e ligações para pesquisar tarifas reais.")
c1, c2, c3 = st.columns(3)
c1.metric("Passageiros", "3 adultos + 1 criança")
c2.metric("Combinações", len(df))
c3.metric("Estadia máxima selecionada", f"{dur_max} dias")

if modo == "Férias escolares":
    st.subheader("📚 Férias escolares em Portugal continental")
    if periodos:
        tabela = pd.DataFrame([{
            "Férias": p["Férias"], "Janela sem aulas": f'{p["Início"]:%d/%m/%Y} a {p["Fim"]:%d/%m/%Y}',
            "Interrupção oficial": f'{p["Oficial início"]:%d/%m/%Y} a {p["Oficial fim"]:%d/%m/%Y}',
            "Estado": "Provisório" if p["Provisório"] else "Calendário nacional",
        } for p in periodos])
        st.dataframe(tabela, hide_index=True, use_container_width=True)
        st.caption("As janelas podem incluir fins de semana adjacentes. Confirma o calendário do agrupamento.")
    else:
        st.info("Sem pausas disponíveis nos filtros selecionados.")

if df.empty:
    st.warning("Não existem viagens compatíveis. Reduz a duração ou a margem para a chegada.")
    st.stop()

df = df.sort_values(["Prioridade", "Ida", "Dias"], ascending=[False, True, False]).reset_index(drop=True)
df["Pesquisar"] = [link_skyscanner(i, v, int(idade), diretos) for i, v in zip(df["Ida"], df["Volta"])]
st.subheader("🗓️ Opções de ida e volta")
mostrar = df.head(150).copy()
mostrar["Ida"] = mostrar["Ida"].map(lambda x: x.strftime("%d/%m/%Y"))
mostrar["Volta"] = mostrar["Volta"].map(lambda x: x.strftime("%d/%m/%Y"))
st.dataframe(mostrar[["Férias", "Ida", "Volta", "Dias", "Pesquisar"]],
             hide_index=True, use_container_width=True,
             column_config={"Pesquisar": st.column_config.LinkColumn("Consultar preço", display_text="Pesquisar ↗")})
st.caption("A ordem dá preferência a dias úteis a meio da semana; não representa uma previsão de preço.")
exportar = df.drop(columns=["Prioridade"]).copy()
exportar["Ida"] = exportar["Ida"].astype(str)
exportar["Volta"] = exportar["Volta"].astype(str)
st.download_button("⬇️ Exportar todas as combinações", exportar.to_csv(index=False, sep=";").encode("utf-8-sig"),
                   "voos_lis_rec_datas.csv", "text/csv")
indice = st.selectbox("Escolher uma combinação", list(range(len(df))),
                      format_func=lambda k: f'{df.at[k, "Férias"]} | {df.at[k, "Ida"]:%d/%m/%Y} → {df.at[k, "Volta"]:%d/%m/%Y} ({df.at[k, "Dias"]} dias)')
sel = df.iloc[indice]
ida, volta = sel["Ida"], sel["Volta"]
col_a, col_b = st.columns(2)
col_a.link_button("🔎 Skyscanner — pesquisar tarifa", sel["Pesquisar"], use_container_width=True)
col_b.link_button("🔎 Google Flights — preencher manualmente",
                  "https://www.google.com/travel/flights?hl=pt-PT", use_container_width=True)
st.info("Confirma a data de chegada a Lisboa: nos voos de regresso do Recife pode ser o dia seguinte. Confirma também preço final, bagagem e escalas.")
if ida > HOJE + timedelta(days=360):
    st.warning("Algumas companhias ainda não vendem bilhetes para datas tão distantes.")

st.divider()
st.subheader("💶 Comparar preços reais")
aba_csv, aba_api = st.tabs(["📄 Orçamentos CSV", "🌐 API Skyscanner (opcional)"])
with aba_csv:
    st.write("Importa tarifas que tenhas obtido. Valores individuais são multiplicados por 3 adultos e 1 criança.")
    st.code("ida,volta,companhia,tipo,preco_adulto_eur,preco_crianca_eur\n2027-03-23,2027-04-01,Exemplo,Direto,850,690",
            language="csv")
    st.caption("O exemplo acima é fictício, apenas para mostrar o formato do CSV.")
    f = st.file_uploader("Carregar ficheiro CSV", type=["csv"])
    if f is not None:
        try:
            orc = importar_orcamentos(f, diretos)
            validas = df[["Ida", "Volta", "Férias"]].rename(columns={"Ida": "ida", "Volta": "volta"})
            conj = orc.merge(validas, on=["ida", "volta"]).sort_values("total_eur")
            if conj.empty:
                st.warning("Nenhum orçamento coincide com as datas da pesquisa.")
            else:
                mais = conj.iloc[0]
                st.success(f'Melhor orçamento importado: {mais["total_eur"]:,.2f} € — {mais["companhia"]}')
                st.dataframe(conj[["Férias", "ida", "volta", "companhia", "tipo", "total_eur"]],
                             hide_index=True, use_container_width=True)
                st.download_button("Exportar comparação", conj.to_csv(index=False, sep=";").encode("utf-8-sig"),
                                   "comparacao_voos.csv", "text/csv")
        except ValueError as ex:
            st.error(str(ex))
with aba_api:
    st.write("Acesso à API Flights Live Prices exige credenciais de parceiro Skyscanner.")
    try:
        chave_guardada = st.secrets.get("SKYSCANNER_API_KEY", "")
    except Exception:
        chave_guardada = ""
    chave = chave_guardada or st.text_input("Chave API (não é guardada no GitHub)", type="password")
    if st.button("Pesquisar preços para estas datas", disabled=not bool(chave)):
        with st.spinner("A consultar tarifas..."):
            try:
                ofertas, finalizada = procurar_api(str(chave), ida, volta, int(idade), diretos)
                st.session_state["resultado_api"] = (ida, volta, int(idade), diretos, ofertas, finalizada)
            except RuntimeError as ex:
                st.error(str(ex))
    resultado = st.session_state.get("resultado_api")
    if resultado and resultado[:4] == (ida, volta, int(idade), diretos):
        ofertas = resultado[4]
        if ofertas:
            st.metric("Menor tarifa familiar devolvida pela API", f'{ofertas[0]["Família (€)"]:,.2f} €')
            st.dataframe(pd.DataFrame(ofertas), hide_index=True, use_container_width=True,
                         column_config={"Reservar": st.column_config.LinkColumn(display_text="Abrir ↗")})
            if any(x["Reservas separadas"] for x in ofertas):
                st.warning("Algumas tarifas exigem reservas separadas: confirma todas antes de pagar.")
        else:
            st.warning("Não foram encontradas tarifas para esta combinação.")
        if not resultado[5]:
            st.caption("A API poderá ter devolvido resultados parciais.")

with st.expander("Fontes, limitações e calendário"):
    st.markdown(f"[Despacho do calendário escolar no Diário da República]({FONTE})")
    st.markdown(f"[Atualização do calendário escolar]({FONTE_2})")
    st.write("Calendário nacional para Portugal continental; estabelecimentos de ensino podem ter adaptações.")
    st.write("O verão de 2028 é provisório: confirma o início oficial das aulas de 2028/2029.")
    st.write("Os preços só aparecem quando importados ou recebidos da API; nenhum valor de exemplo é uma oferta real.")
