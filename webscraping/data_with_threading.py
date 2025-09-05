import threading
import requests
import time

datalist:list=[]

def getDatafromInternet(url: str):
    print(url)
    data = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        },
    )
    datalist.append(data.text)


for x in range(1, 20000):
    url = f"https://www.naukri.com/jobs-in-gurgaon-{x}"
    t = threading.Thread(target=getDatafromInternet, args=(url,))
    t.start()
