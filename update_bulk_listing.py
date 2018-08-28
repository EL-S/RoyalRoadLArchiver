# import libraries
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def init():
    try:
        with open("processed.txt", "r") as processed_object:
            pass
    except FileNotFoundError:
        with open("processed.txt", "w") as processed_object:
            processed_object.write("")
            return init()
    try:
        with open("dead_processed.txt", "r") as dead_processed_object:
            pass
    except FileNotFoundError:
        with open("dead_processed.txt", "w") as dead_processed_object:
            dead_processed_object.write("")
            return init()

def get_alive_index(url):
    # query the website and return the html to the variable ‘page’
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        page = urlopen(req)
    except:
        print("Couldn't load:",url)
    if page:    
        # parse the html using beautiful soup and store in variable `soup`
        soup = BeautifulSoup(page, 'html.parser')

        try:
            alive = soup.find('div', attrs={'class': 'number font-red-sunglo'})
            if alive == None:
                return True
            else:
                return False
        except:
            print("umm",url) #no html or data transfered

searching = 0
links = []
dead_links = []
x = 0 #starting id number
init()

while searching == 0:
    url = "http://www.royalroadl.com/fiction/" + str(x)
    status = get_alive_index(url)
    if status == True:
        print("alive", url)
        links.append(url)
    else:
        print("dead", url)
        dead_links.append(url)
    if (x >= 30): #maximum id to go to, (21000 @ 8/28/2018) check the new releases on the website for an estimate to use (in the url)
        searching = 1
    x += 1

with open("processed.txt", "w") as processed_object:
    for i in links:
        processed_object.write(i+"\n")
        #write to file with this new line
with open("dead_processed.txt", "w") as dead_processed_object:
    for i in dead_links:
        dead_processed_object.write(i+"\n")
        #write to file with this new line

print("complete, run bulk download now")


        
