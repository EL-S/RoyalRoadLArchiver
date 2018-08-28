import time
from urllib.request import Request, urlopen
import http.client  # or http.client if you're on Python 3
http.client._MAXHEADERS = 10000
from bs4 import BeautifulSoup

latest = "http://www.royalroadl.com/fictions/latest-updates?page="
pages_to_check = 30

def get_html(url):
    # query the website and return the html to the variable ‘page’
    try:
        #print("attempt request")

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, None, 10) as response: # 2.5 second timeout before retry
           page = response.read()
        #print("request succeed")
        if page == None:
            print("internet issue 2")
            return get_html(url)
        else:
            return page
    except Exception as e:
        print(e)
        # sleep for a bit in case that helps
        time.sleep(1)
        print("internet issue")
        # try again
        print(url)
        return get_html(url)

def soup_lookup(html, tag, prop, prop_val, type_val = None, prop2 = None, prop3 = None):
    d = 0
    soup = BeautifulSoup(html, 'lxml')
    element = []
    if type_val == "get_all":
        y = soup.findAll(tag, attrs={prop: prop_val})
        y3 = []
        for x in y:
            y2 = x.find(prop3)
            y3.append(y2)
        for i in range(0, len(y3)):
            try:
                element.append(y3[i].get(prop2))
            except AttributeError:
                print("Error")
                return None
            else:
                d += 1
        return element
    else:
        element.append(soup.find(tag, attrs={prop: prop_val}))
    if type_val == "get":
        try:
            element.append(element[0].get(prop2))
        except AttributeError:
            print("Latest Chapter")
            return None
    elif type_val == "strip":
        element.append(element[0].text.strip())
    return element


def check_for_updates():
    fictions = []
    for i in range(1,pages_to_check):
        url = latest + str(i)
        html = get_html(url)
        elements = soup_lookup(html, "h2", "class", "fiction-title", "get_all", "href", "a")
        for x in elements:
            fictions.append(x)
    with open("updatequeue.txt", "r") as file:
        for x in file:
            fictions.append(x)
    fictions = list(set(fictions))
    with open("updatequeue.txt", "w") as file:
        for x in fictions:
            file.write("http://www.royalroadl.com"+x+"\n")

# potential future update to combine all scripts
#def update_fictions():  
#    for x in fictions: 
#        print("do the thing")  

check_for_updates()
    
    
print("done")
