from DataApi import DataApi, quantosToken 

api = DataApi(addr="tcp://data.tushare.org:8910")
df, msg = api.login(quantosToken.phone, quantosToken.key)

symbol = 'T1712.CFE, TF1712.CFE, rb1712.SHF'
fields = 'open,high,low,last,volume'

df, msg = api.quote(symbol=symbol, fields=fields)
print(df)
print(msg)