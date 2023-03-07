# ir-acoes

This is my personal stock taxex calculator.

It only makes sense for residents of Brazil.

# Calculadora de imposto de renda (ações)

Scripts para ajudar no cálculo do Imposto de Renda.

## Passos

É utilizada a linguagem Python 3.10 e os SO alvo é o Ubuntu

- extrato da B3 (site) necessário
  - entrar em negociações
  - filtrar por primeiro dia 01/Jan a 31/Dez
  - filtrar por compra e venda de ações
  - exportar em formato Excel
- preencher as posições anteriores em 'posicoes-iniciais.json', se você entrou no ano comprado
Exemplo:

{
  "PETR4": {
      "preco-medio": "10.45135712",
      "quantidade": "1000"
  },
  "ITUB4": {
      "preco-medio": "21.12",
      "quantidade": "3000"
  }
}

- criar um novo venv
- pip install -r requirements.txt
