# ✈️ Lisboa ↔ Recife · Férias Escolares

## Versão recomendada: HTML (sem instalação)

A versão móvel é o ficheiro **`index.html`**, feito apenas com HTML, CSS e JavaScript. Funciona num navegador sem servidor Python.

### Publicar gratuitamente no GitHub Pages

1. Abrir **https://github.com/Fdorotea1/voos-recife-ferias/settings/pages**.
2. Em **Build and deployment → Source**, escolher **Deploy from a branch**.
3. Em **Branch**, escolher **main** e **/(root)** e carregar em **Save**.
4. Quando a publicação terminar, abrir **https://fdorotea1.github.io/voos-recife-ferias/** no telemóvel.
5. No navegador, usar a opção **Adicionar ao ecrã principal** para guardar o atalho.

A aplicação calcula combinações de datas nas férias escolares de 2026/2027 e 2027/2028, respeitando os diferentes anos de escolaridade, a duração máxima configurável de 30 dias e uma margem de regresso antes das aulas. Permite comparar datas no Skyscanner e Google Flights, registar preços familiares observados e exportar CSV. Nas férias mais curtas o calendário escolar limita naturalmente a duração disponível.

### Calendário específico do Agrupamento de Escolas do Restelo — 2026/2027

Validado a partir do documento **Calendário Escolar 2026.2027.pdf** do Agrupamento de Escolas do Restelo, assinado a 1 de setembro de 2026:

- 1.º período termina a **15/12/2026**; 2.º período inicia a **04/01/2027**.
- Carnaval: **08 a 10/02/2027**.
- 2.º período termina a **19/03/2027**, e o 3.º começa a **05/04/2027**. Por isso, a janela sem aulas na Páscoa é **20/03 a 04/04/2027**, incluindo fins de semana. A interrupção letiva oficial é de 22/03 a 02/04.
- Fim de aulas em **04/06/2027** (9.º, 11.º, 12.º), **11/06/2027** (5.º–8.º e 10.º), **30/06/2027** (pré-escolar e 1.º ciclo). O PDF contém a gralha «30 de junho de 2026»; o ano correto é **2027**, conforme o calendário nacional.
- Para **2027/2028**, a versão HTML usa o calendário geral e assinala que **não foi confirmado o documento específico do Restelo**.

### Calculadora de férias — versão HTML

A calculadora está no mesmo `index.html`, sem exigir serviços externos. Por defeito utiliza **1.100 € de faturação semanal conjunta, seis dias de trabalho, folga à segunda-feira e 30 € diários de energia/GPL**. Permite escolher o primeiro dia de férias, o voo de regresso, a chegada a Lisboa e o **primeiro dia de regresso ao trabalho**, que é a data relevante para contar os dias de rendimento não gerado.

O cálculo apresenta separadamente **dias sem trabalhar, faturação não realizada, energia/GPL poupados e rendimento não gerado**; permite ainda somar o preço dos voos para quatro passageiros e outras despesas introduzidas pelo utilizador. Os valores podem ser personalizados e são guardados localmente neste dispositivo.

**Não apresenta preços simulados.** As datas e filtros do Skyscanner e Google Flights devem ser confirmados após abrir as ligações. O montante não gerado não corresponde necessariamente ao lucro contabilístico, pois não inclui impostos ou outros custos variáveis.

Fonte oficial: https://diariodarepublica.pt/dr/detalhe/despacho/8368-2024-873447631 (e alterações posteriores).

---

## Versão anterior: Streamlit

A versão Python mantém-se disponível nos ficheiros `app.py` e `requirements.txt`.

Para a publicar, é necessário usar **https://share.streamlit.io/**, escolher este repositório, a branch `main` e o ficheiro `app.py`. A integração opcional com preços através da API Skyscanner requer credenciais de parceiro guardadas nos segredos do Streamlit, nunca no GitHub.

**Recomendação:** para utilização familiar no telemóvel e comparação manual de preços, utilizar a versão HTML.
