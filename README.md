# ir-acoes

This is my personal tax calculator for stocks. It only makes sense for **residents of Brazil**. 

# Calculadora de imposto de renda (ações)

Scripts para ajudar no cálculo do Imposto de Renda.

## Passos

É utilizada a linguagem Python 3.10 e os SO alvo é o Ubuntu

- extrato da B3 (site) necessário
  - entrar em negociações
  - filtrar por primeiro dia 01/Jan a 31/Dez
  - filtrar por compra e venda de ações
  - exportar em formato Excel
  - mover o arquivo para a pasta raiz do projeto
- preencher as posições anteriores em 'posicoes-iniciais.json', se você entrou no ano comprado
Exemplo:
```
{
  "PETR4": {
      "total": 30151.21,
      "quantidade": 1000
  },
  "ITUB4": {
      "total": 6336,
      "quantidade": 300
  }
}
```
- caso você não possua nenhuma ação no ano anterior, apenas deixe o **JSON vazio**
- criar um novo venv
- pip install -r requirements.txt
