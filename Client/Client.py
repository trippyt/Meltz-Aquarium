import requests
payload = {'username':'admin','password':'password'}

session = requests.Session()
resp = session.post('http://trippyt.hopto.org/login',data=payload)
print(resp)

stt = session.get('http://trippyt.hopto.org/schedule')
light_state = stt.json()
print(light_state['value'])

light_state['value'][4] = 'day'
session.post('http://trippyt.hopto.org/schedule', data=light_state)
resp = session.get('http://trippyt.hopto.org/schedule')
light_state = resp.json()
print(light_state['value'])