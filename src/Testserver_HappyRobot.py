import requests
###Test server

proxy_url = "http://127.0.0.1:5000/verify_dot"

dot_number = "687592"


response = requests.get(url=proxy_url,params={"dot_number": dot_number})

if response.status_code == 200:
    print("Gettttt")

else:
    print("Errrrr")