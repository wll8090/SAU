
with open('./config.ini','r') as arq:
    data=arq.read().strip()
    data=data.replace('"','')
    data=data.split('\n')
    data=[i.split(':') for i in data if i and not i.startswith("#")]
    data={a.strip():b.strip() for a,b in data}
    globals().update(data)
