# test.py — arquivo temporário para testar a conexão com o FRED
# Pode deletar depois que confirmar que funcionou

from utils.fetchers import get_series

# Vamos buscar a taxa de juros dos EUA desde 2020
data = get_series("FEDFUNDS", start_date="2020-01-01")

# Imprime os últimos 5 valores
print(data.tail(5))