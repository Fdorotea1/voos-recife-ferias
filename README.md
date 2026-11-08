# ✈️ Voos Lisboa ↔ Recife · Férias Escolares

Aplicação Streamlit em português de Portugal para procurar datas de ida e volta (até 10 dias) para **3 adultos e 1 criança**.

## Funcionalidades

- Calendário nacional de férias escolares 2026/2027 e 2027/2028, adaptado ao ciclo/ano de escolaridade.
- Comparação de combinações de datas e margem para chegada a Portugal após o voo noturno.
- Links de pesquisa no Skyscanner; Google Flights abre para configuração manual.
- Importação de preços reais em CSV, com cálculo do preço total da família.
- Consulta opcional da API Skyscanner Flights Live Prices (requer aprovação como parceiro).
- Exportação das combinações de viagem em CSV.

**Importante:** nenhum preço simulado é apresentado como tarifa disponível. O verão de 2028 está marcado como provisório. Os calendários locais e os horários efetivos dos voos devem ser confirmados antes de reservar.

## Publicar no Streamlit Community Cloud

1. Abrir https://share.streamlit.io/ e autenticar com GitHub.
2. Selecionar **New app** / **Deploy a public app from GitHub**.
3. Escolher o repositório `Fdorotea1/voos-recife-ferias`, a branch `main` e o caminho `app.py`.
4. Clicar **Deploy**.

O ficheiro `requirements.txt` define as dependências; não é preciso instalar Python no telemóvel.

## API opcional

Se tiveres credenciais de parceiro, adiciona `SKYSCANNER_API_KEY` aos **Secrets** nas definições da aplicação do Streamlit. Nunca publiques chaves no GitHub.

## CSV de orçamentos

Aceita cabeçalhos:

```csv
ida,volta,companhia,tipo,preco_adulto_eur,preco_crianca_eur
2027-03-23,2027-04-01,Exemplo,Direto,850,690
```

ou `preco_total_eur` no lugar dos dois preços individuais. Estes valores são ilustrativos.
