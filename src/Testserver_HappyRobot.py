import requests
###Test server

proxy_url = "http://127.0.0.1:5000/verify_dot"
proxy_url_2 = "http://127.0.0.1:5000//loads/REF17029"
dot_number = "87592"


response = requests.get(url=proxy_url,params={"dot_number": dot_number})

if response.status_code == 200:
    print("Gettttt")
    print(response.json())

else:
    print("Errrrr")


# response = requests.get(url=proxy_url_2)

# if response.status_code == 200:
#     print("Gettttt")
#     print(response.json())


# else:
#     print("Errrrr")

