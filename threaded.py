from bs4 import BeautifulSoup
from tornado import ioloop, httpclient
from datetime import datetime
import re
import os

i = 0
chapters_downloaded = []
chapters_html = {}
fiction_html = ""
directory = "webnovels/"

def init():
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_fiction_info(fiction_id): #finished
    http_client = httpclient.HTTPClient()
    url = "https://www.royalroad.com/fiction/"+str(fiction_id)
    html = http_client.fetch(url).body.decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    title = get_fiction_title(soup)
    cover_image = get_fiction_cover_image(soup)
    author = get_fiction_author(soup)
    description = get_fiction_description(soup)
    ratings = get_fiction_rating(soup)
    chapter_links = get_chapter_links(soup)
    chapter_amount = len(chapter_links)
    #print(url,title,cover_image,author,description,ratings,chapter_links,chapter_amount)
    return url,title,cover_image,author,description,ratings,chapter_links,chapter_amount

def get_fiction_title(soup): #finished
    title = soup.find('h1', attrs={'property': 'name'}).text.strip()
    return title

def get_fiction_cover_image(soup): #finished
    cover_image = soup.find('img', attrs={'property': 'image'}).get('src')
    if cover_image == "/Content/Images/nocover.png":
        cover_image = "http://www.royalroadl.com/content/Images/nocover.png"
    return cover_image

def get_fiction_author(soup): #finished
    author = soup.find('span', attrs={'property': 'name'}).text.strip()
    if author == "":
        author = "NONE"
    return author

def get_fiction_description(soup): #finished
    description = soup.find('div', attrs={'property': 'description'}).text.strip()
    if description == "":
        description = "No Description"
    return description

def get_fiction_rating(soup): #finished
    overall_rating = soup.find('meta', attrs={'property': 'ratingValue'}).get("content")
    best_rating = soup.find('meta', attrs={'property': 'bestRating'}).get("content")
    rating_count = soup.find('meta', attrs={'property': 'ratingCount'}).get("content")
    style_rating = soup.find('span', attrs={'data-original-title': 'Style Score'}).get("data-content")
    story_rating = soup.find('span', attrs={'data-original-title': 'Story Score'}).get("data-content")
    character_rating = soup.find('span', attrs={'data-original-title': 'Character Score'}).get("data-content")
    grammar_rating = soup.find('span', attrs={'data-original-title': 'Grammar Score'}).get("data-content")
    rating = [overall_rating,best_rating,rating_count,style_rating,story_rating,character_rating,grammar_rating]
    return rating

def get_chapter_links(soup): #finished
    chapter_links = []
    chapter_links_tag = soup.findAll('tr', attrs={'style': 'cursor: pointer'})
    for tag in chapter_links_tag:
        chapter_link = tag.get("data-url")
        chapter_links.append(chapter_link)
    return chapter_links

def get_chapters(chapter_links):
    global chapters_downloaded,chapters_html,fiction_html
    chapters_downloaded = []
    chapters_html = {}
    fiction_html = ""
    http_client = httpclient.AsyncHTTPClient(force_instance=True,defaults=dict(user_agent="Mozilla/5.0"),max_clients=2)
    for chapter in chapter_links:
        global i
        i += 1
        url = "https://www.royalroad.com/"+str(chapter)
        http_client.fetch(url.strip(),handle_chapter_response, method='GET',connect_timeout=10000,request_timeout=10000)
    ioloop.IOLoop.instance().start()

def get_chapter_content(html):
    soup = BeautifulSoup(html, "lxml")
    chapter_title = "<center>" + str(soup.find('h1', attrs={'style': 'margin-top: 10px','class': 'font-white'})) + "</center>"
    content_html = str(soup.find('div', attrs={'class': 'chapter-inner chapter-content'}))
    print(chapter_title)
    return content_html,chapter_title

def save_to_hdd(fiction_html):
    global url,title,cover_image,author,description,ratings,chapter_links,chapter_amount
    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    data = "<center><img src='" + cover_image + "'><b><h1> \"<a href='" + url + "'>" + str(title) + "</a>\" by \"" + str(author) + "\"</h1></b><br><h2>Last updated: " + time + "</h2></center><br><h3>Description: " + str(description) + "</h3><br>" + fiction_html
    title_clean = re.sub(r'[\\/*?:"<>|]',"",title)
    author_clean = re.sub(r'[\\/*?:"<>|]',"",author)
    print(title_clean + " - " + author_clean + ".html")
    file_name = title_clean + " - " + author_clean + ".html"
    full_path = directory + file_name
    with open(full_path, "w", encoding="utf-8") as file_webnovel:
        file_webnovel.write(data)
    
def handle_chapter_response(response):
    if response.code == 599:
        print(response.effective_url)
        http_client.fetch(response.effective_url.strip(), handle_request, method='GET',connect_timeout=10000,request_timeout=10000)
    else:
        global i,chapters_downloaded,chapters_html,fiction_html
        html = response.body.decode('utf-8')
        url = response.effective_url
        chapter_id = int(url.split("/")[-2])
        chapters_downloaded.append(chapter_id)
        html = get_chapter_content(html)
        chapters_html[chapter_id] = html
        print(url)
        i -= 1
        if i == 0: #all chapters downloaded for the fiction
            #evoke a function with the complete fiction html
            chapters_downloaded.sort(key=int)
            chp = 0
            for chp_id in chapters_downloaded:
                chp += 1
                fiction_html = fiction_html + "(" + str(chp) + ")" + chapters_html[chp_id][1] + chapters_html[chp_id][0]
            save_to_hdd(fiction_html)
            print("done")
            ioloop.IOLoop.instance().stop()
print("uwu")
init()
url,title,cover_image,author,description,ratings,chapter_links,chapter_amount = get_fiction_info(20887)
get_chapters(chapter_links)
