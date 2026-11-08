# ✈️ Lisboa ↔ Recife · Férias Escolares

## Versão recomendada: HTML (sem instalação)

A versão móvel é o ficheiro **`index.html`**, feito apenas com HTML, CSS e JavaScript. Funciona num navegador sem servidor Python.

### Publicar gratuitamente no GitHub Pages

1. Abrir **https://github.com/Fdorotea1/voos-recife-ferias/settings/pages**.
2. Em **Build and deployment → Source**, escolher **Deploy from a branch**.
3. Em **Branch**, escolher **main** e **/(root)** e carregar em **Save**.
4. Quando a publicação terminar, abrir **https://fdorotea1.github.io/voos-recife-ferias/** no telemóvel.
5. No navegador, usar a opção **Adicionar ao ecrã principal** para guardar o atalho.

A aplicação calcula combinações de datas nas férias escolares de 2026/2027 e 2027/2028, respeitando os diferentes anos de escolaridade, a duração máxima de 10 dias e uma margem de regresso antes das aulas. Permite comparar datas no Skyscanner e Google Flights e exportar CSV.

**Não apresenta preços simulados.** As datas e filtros do Skyscanner e Google Flights devem ser confirmados após abrir as ligações. As escolas podem ter um calendário local ou semestral diferente.

Fonte oficial: https://diariodarepublica.pt/dr/detalhe/despacho/8368-2024-873447631 (e alterações posteriores).

---

## Versão anterior: Streamlit

A versão Python mantém-se disponível nos ficheiros `app.py` e `requirements.txt`.

Para a publicar, é necessário usar **https://share.streamlit.io/**, escolher este repositório, a branch `main` e o ficheiro `app.py`. A integração opcional com preços através da API Skyscanner requer credenciais de parceiro guardadas nos segredos do Streamlit, nunca no GitHub.

**Recomendação:** para utilização familiar no telemóvel e comparação manual de preços, utilizar a versão HTML.
