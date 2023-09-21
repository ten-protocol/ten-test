import urllib.request

for i in range(50):
    page = urllib.request.urlopen('https://testnet.obscu.ro/v1/join/')
    print(page.read())