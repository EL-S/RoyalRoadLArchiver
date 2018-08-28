# import libraries
import os
from urllib.request import Request, urlopen
import http.client  # or http.client if you're on Python 3
http.client._MAXHEADERS = 10000
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
#import pdb; pdb.set_trace()
import lxml
import time
import sys
sys.setrecursionlimit(10000)# It sets recursion limit to 10000

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def init():
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        with open("updatequeue.txt", "r") as queue_object:
            pass
    except FileNotFoundError:
        with open("updatequeue.txt", "w") as queue_object:
            queue_object.write("")
            return init()
    try:
        with open("updatechapters.txt", "r") as chapters_object:
            pass
    except FileNotFoundError:
        with open("updatechapters.txt", "w") as chapters_object:
            chapters_object.write("")
            return init()
    try:
        with open("updateindex.txt", "r") as index_number_object:
            pass
    except FileNotFoundError:
        with open("updateindex.txt", "w") as index_number_object:
            index_number_object.write("0")
            return init()

def get_index_number():
    try:
        with open("updateindex.txt", "r") as index_number_object:
            index_number = int(index_number_object.read())
            return index_number
    except FileNotFoundError:
        with open("updateindex.txt", "w") as index_number_object:
            index_number_object.write("0")
            return get_index_number()

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

def clean_image(cover):
    if cover == "/Content/Images/nocover.png":
        cover = "http://www.royalroadl.com/content/Images/nocover.png"
    return "<img src='" + cover + "'>"

def clean_desc(desc):
    if desc[1] == "":
        desc = '<div class="hidden-content" property="description">No Synopsis</div>'
    else:
        desc = desc[0]
    return desc
    

def collect_data(html):
    first_chapter_link = soup_lookup(html, "tr", "style", "cursor: pointer", "get", "data-url") #[1]
    if not first_chapter_link:
        print("no chapters")
        return None
    else:
        first_chapter_link = "https://www.royalroadl.com" + first_chapter_link[1]
    cover = soup_lookup(html, "img", "property", "image", "get", "src")[1]
    title = soup_lookup(html, "h1", "property", "name", "strip")[1]
    author = soup_lookup(html, "span", "property", "name", "strip")[1]
    desc = soup_lookup(html, "div", "property", "description", "strip") #not a mistake

    cover = clean_image(cover)
    desc = clean_desc(desc)

    download_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return [first_chapter_link, cover, title, author, desc, download_time]
    
def start(url):
    html = get_html(url)
    print("downloaded index:", url)
    return collect_data(html)

#content_link needs to be []

def download_story(content_link, content_html = [], c = 0):
    print("chp:", c+1)
    if c == 0:
        content_html = [] #THE HTML IS NOT RESETTING EVERY FUNCTION CALL UNLESS THIS LINE IS HERE
    html = get_html(content_link[c])
    content_html.append(soup_lookup(html, "div", "class", "chapter-inner chapter-content")[0])
    if c == 0:
        content_link = [content_link[0]]
    try:
        next_link = "http://www.royalroadl.com" + str(soup_lookup(html, "link", "rel", "next", "get", "href")[1])
    except TypeError:
        return [content_link, content_html]
    else:
        if next_link in content_link:
            print("Already downloaded that page", next_link)
            return [content_link, content_html]
    content_link.append(next_link)
    c += 1
    return download_story(content_link, content_html, c)

def to_html(data, html_array, c = 1):
    x = None
    for x in html_array[1]:
        chapter_title = re.sub(r"\-", r" ", html_array[0][c-1].split("/")[-1]).title()
        #does regex on the chapters url for a stripped chapter title
        
        chapter_html = "<center><b><h1>("+str(c)+")" + " " + str(chapter_title) + "</h1></b></center><br>" + str(x)
        if c == 1:

            entire_story = "<link rel='stylesheet' href='styles/tables.css'><center>" + str(data[1]) + "<b><h1> \"<a href='" + str(data[0]) + "'>" + str(data[2]) + "</a>\" by \"" + str(data[3]) + "\"</h1></b><br><h2>Last updated: " + str(data[5]) + "</h2></center><br><h3>Synopsis: " + str(data[4]) + "</h3><br>" + str(chapter_html)
        else:
            entire_story = entire_story + chapter_html
        c += 1
    try:
      entire_story
    except NameError:
        print("broken vars")
        return to_html(data, html, c = 1)
    else:
      return entire_story

def to_standard_characters(non_standard):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    return non_standard.translate(non_bmp_map)

def save_to_hdd(html,data,directory):
    title = re.sub(r'[\\/*?:"<>|]',"",data[2])
    author = re.sub(r'[\\/*?:"<>|]',"",data[3])
    file_name = title + " - " + author + ".html"
    full_path = directory + file_name
    print(to_standard_characters(file_name)) #doesn't suppose Non-BMP characters without above code
    full_path = directory + file_name
    with open(full_path, "w", encoding="utf-8") as file_book:
        file_book.write(html)
    
#soup_lookup(html, "h1", "property", "name", "get", "src")
# returns array with [0] and [1]
# 0 is html
# 1 is the value of a property of a tag

def check_for_updates(val = None):
    if val:
        latest = "http://www.royalroadl.com/fictions/latest-updates?page="
        pages_to_check = 1
        fictions = []
        for i in range(1,pages_to_check+1):
            url = latest + str(i)
            html = get_html(url)
            elements = soup_lookup(html, "h2", "class", "fiction-title", "get_all", "href", "a")
            chapters = soup_lookup(html, "li", "class", "list-item", "get_all", "href", "a")
            chapters_test = [x[9:] for x in chapters]
            chapters_test2 = []
            for x in chapters_test:
                chapters_test2.append(re.search(r"[^/]+", x).group())
            prev_y = None
            c = 0
            new_chapter_titles_index = []
            for y in chapters_test2:
                if y == prev_y:
                    pass
                else:
                    new_chapter_titles_index.append(chapters[c])
                c += 1
                prev_y = y
                
            fictions4 = []
            for x in elements[:5]:
                fictions.append(x)
            for y in new_chapter_titles_index[:5]:
                fictions4.append(y)
        fictions2 = []
        fictions3 = []
        with open("updatequeue.txt", "r") as file2:
            for x in file2:
                fictions2.append(x[25:-1])
        with open("updatechapters.txt", "r") as file:
            for x in file:
                fictions3.append(x[25:-1])
        c = 0
        download = []

        for x in fictions:
            same_fiction = False
            same_chapter = False
            try:
                if x == fictions2[c]:
                    same_fiction = True
                if fictions3[c] == fictions4[c]:
                    same_chapter = True
            except Exception as e:
                print(e)
            finally:
                if same_fiction and same_chapter:
                    pass
                else:
                    download.append(x)
            c += 1
        if download:
            with open("updatequeue.txt", "w") as file:
                for x in download:
                    file.write("http://www.royalroadl.com"+x+"\n")
            with open("updatechapters.txt", "w") as file:
                for x in fictions4:
                    file.write("http://www.royalroadl.com"+x+"\n")
        else:
            print("No updates")
            time.sleep(5)
            return check_for_updates("minimal")
        
    else:
        latest = "http://www.royalroadl.com/fictions/latest-updates?page="
        pages_to_check = 4
        fictions = []
        for i in range(1,pages_to_check+1):
            url = latest + str(i)
            html = get_html(url)
            elements = soup_lookup(html, "h2", "class", "fiction-title", "get_all", "href", "a")
            for x in elements:
                fictions.append(x)
        with open("updatequeue.txt", "r") as file:
            for x in file:
                fictions.append(x[25:-1])
        fictions = list(set(fictions))
        with open("updatequeue.txt", "w") as file:
            for x in fictions:
                file.write("http://www.royalroadl.com"+x+"\n")

def update_fictions():
    index_number = get_index_number()

    file_len2 = file_len("updatequeue.txt")
    print(file_len2,"fictions queued")
    prev = None

    with open("updatequeue.txt", "r") as links_raw:
        links_array = links_raw.readlines()
        for i in range(index_number,file_len2):
            if prev != links_array[i-1] and index_number != 0:
                print("A jump has occured")
            #print(links_array[i])
            url = None
            html_array = None
            data = None
            url = links_array[i]
            data = start(url)
            #                    0                  1      2      3       4     5
            #returns array with [first_chapter_link, cover, title, author, desc, download_time]
            if data is not None:
                print("collected data")
                html_array = download_story(data)
                #returns array with [[content_link],[content_html]]
                html = to_html(data, html_array)
                #pure html
                save_to_hdd(html,data,directory)
                #finished, begin next story
                print("Complete\n")
            else:
                print("no chapters")
            prev = links_array[i]
            with open("updateindex.txt", "w") as index_number_object:
                index_number_object.write(str(i+1))
    print("done updating")
val = None
directory = "updates/"
init()
while True:
    print("checking for updates")
    val = "minimal"
    check_for_updates(val)
    print("updating...")
    update_fictions()
    with open("updateindex.txt", "w") as index_number_object:
        index_number_object.write(str(0))
    if val == None:
        with open("updatequeue.txt", "w") as updatequeue:
            updatequeue.write("")
    
print("It stopped")



