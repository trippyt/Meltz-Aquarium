import requests
payload = {'USERNAME':'rpi3','admin':'password'}

session = requests.Session()
resp = session.post('http://trippyt.hopto.org/login',data=payload)
print(resp)
