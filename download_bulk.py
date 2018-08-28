# import libraries
import os
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re

def init():
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        with open("processed.txt", "r") as processed_object:
            pass
    except FileNotFoundError:
        with open("processed.txt", "w") as processed_object:
            processed_object.write("")
            return init()
    try:
        with open("broken.txt", "r") as broken_object:
            pass
    except FileNotFoundError:
        with open("broken.txt", "w") as broken_object:
            broken_object.write("")
            return init()
    try:
        with open("loading.txt", "r") as loading_object:
            pass
    except FileNotFoundError:
        with open("loading.txt", "w") as loading_object:
            loading_object.write("")
            return init()
    try:
        with open("loadingchapter.txt", "r") as loadingchapter_object:
            pass
    except FileNotFoundError:
        with open("loadingchapter.txt", "w") as loadingchapter_object:
            loadingchapter_object.write("")
            return init()

def get_index(url):
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
            index = soup.find('a', attrs={'class': 'btn btn-block btn-primary margin-bottom-5'})
            if index != None:
                try:
                    index_link = index.get('href')
                    return "http://www.royalroadl.com" + index_link
                except:
                    print("Couldn't find index",url)
            else:
                print("no index")
        except:
            print("Couldn't find index button",url)

def first_chapter(url):
    # query the website and return the html to the variable ‘page’
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        page = urlopen(req)
        if page:    
            # parse the html using beautiful soup and store in variable `soup`
            soup = BeautifulSoup(page, 'html.parser')

            try:
                title = soup.find('h1', attrs={'property': 'name'})
                if title != None:
                    try:
                        title_str = title.text.strip()
                        #print("Title:",title_str)
                    except:
                        print("no title",url)
                else:
                    print("no title 2")
            except:
                print("Couldn't find title",url)

            try:
                desc_html = soup.find('div', attrs={'property': 'description'})
                desc = desc_html.text.strip()
                
                if desc == "":
                    desc_html = '<div class="hidden-content" property="description">No Synopsis</div>'
            except:
                print("Couldn't find desc",url)
                desc_html = '<div class="hidden-content" property="description">No Synopsis</div>'
            
            try:
                author = soup.find('span', attrs={'property': 'name'})
                if author != None:
                    try:
                        author_str = author.text.strip()
                        #print("Author:",author_str)
                    except:
                        print("no author",url)
                else:
                    print("no author 2")
            except:
                print("Couldn't find author",url)

            try:
                cover = soup.find('img', attrs={'property': 'image'})
                if cover != None:
                    try:
                        cover_link = cover.get('src')
                        #print("cover:",cover)
                        #print("cover src:",cover_link)
                        if cover_link == "/Content/Images/nocover.png":
                            cover_link = "http://www.royalroadl.com/content/Images/nocover.png"
                        cover_html = "<img src='" + cover_link + "'>"
                    except:
                        print("no image",url)
                else:
                    print("no image 2")
            except:
                print("Couldn't find image",url)
            
            try:
                first_chapter = soup.find('tr', attrs={'style': 'cursor: pointer'})
                if first_chapter != None:
                    try:
                        first_chapter_link = first_chapter.get('data-url')
                        return ["http://www.royalroadl.com" + first_chapter_link,title_str,author_str,cover_html,desc_html]
                    except:
                        print("Couldn't find first chapter",url)
                else:
                    print("no chapters? ",url)
                    with open("broken.txt", "a") as file2:
                        file2.write(url)
                    return None
            except:
                print("Couldn't find first chapter",url)
    except:
        print("Couldn't load:",url)
        with open("loading.txt", "a") as file3:
            file3.write(url)
        first_chapter(url)
        


def collect(url,content_html = [[],[]], c = 0):
    print("chapter", c+1)
    if c == 0:
        content_html = [[],[url]]
    # query the website and return the html to the variable ‘page’
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    c_old = c
    old_content_html = content_html
    try:
        page = urlopen(req)
        if page:    
            # parse the html using beautiful soup and store in variable `soup`
            soup = BeautifulSoup(page, 'html.parser')

            # Take out the <div> of name and get its value
            current_html = soup.find('div', attrs={'class': 'chapter-inner chapter-content'})
            content_html[0].append(current_html)
            #print(content_html[0][c])
            content = content_html[0][c].text.strip() # strip() is used to remove starting and trailing

            try:
                next_chapter = soup.find('link', attrs={'rel': 'next'})
                if next_chapter != None:
                    try:
                        next_link =  "http://www.royalroadl.com" + next_chapter.get('href')
                        content_html[1].append(next_link)
                        #print(next_link)
                        c += 1
                        collect(next_link,content_html,c)
                    except:
                        with open("loadingchapter.txt", "a") as file4:
                            file4.write(url)
                        first_chapter(url)
                        print("Couldn't find next chapter link",url)
                        collect(url,old_content_html, c_old)
                else:
                    #print("Latest chapter")
                    return content_html
            except:
                print("Couldn't find next chapter button",url)
    except:
        print("Couldn't load:",url)
        collect(url,old_content_html, c_old)
    return content_html

def tohtml(content, booktitle, author, cover, desc, url, time, c = 1):
    for x in content[0]:
        title = re.sub(r"\-", r" ", content[1][c-1].split("/")[-1]).title()
        this_chapter = "<center><b><h1>("+str(c)+")" + " " + str(title) + "</h1></b></center><br>" + str(x)
        if c == 1:
            final = "<center>" + cover + "<b><h1> \"<a href='" + first_chapter2[0] + "'>" + str(booktitle) + "</a>\" by \"" + str(author) + "\"</h1></b><br><h2>Last updated: " + time + "</h2></center><br><h3>Synopsis: " + str(desc) + "</h3><br>" + this_chapter
        else:
            final = final + this_chapter
        c += 1
    return final

def clear_vars():
        index = None
        first_chapter = None
        content = None
        time = None
        html = None
        title_clean = None
        author_clean = None
        file_name = None
        full_path = None

directory = "webnovels/"

init()
with open("processed.txt", "r") as stories:
    for line in stories:
        clear_vars()
        index = line
        print("Attempting...",line)
        first_chapter2 = first_chapter(index)
        #print(first_chapter2)
        if first_chapter2 != None:
            content = collect(first_chapter2[0])
            time = datetime.now().strftime("%Y-%m-%d %H:%M")
            html = tohtml(content,first_chapter2[1],first_chapter2[2],first_chapter2[3],first_chapter2[4],first_chapter2[0],time)
            #print(html)
            #print(first_chapter2[1] + " - " + first_chapter2[2] + ".html")
            title_clean = re.sub(r'[\\/*?:"<>|]',"",first_chapter2[1])
            author_clean = re.sub(r'[\\/*?:"<>|]',"",first_chapter2[2])
            print(title_clean + " - " + author_clean + ".html")
            file_name = title_clean + " - " + author_clean + ".html"
            full_path = directory + file_name
            with open(full_path, "w", encoding="utf-8") as file_book:
                file_book.write(html)
            print(content[1][0])
            print(time)
            with open('processed.txt', 'r+') as f: #open in read / write mode
                f.readline() #read the first line and throw it out
                data = f.read() #read the rest
                f.seek(0) #set the cursor to the top of the file
                f.write(data) #write the data back
                f.truncate() #set the file size to the current size

print("complete")
#check for the index page

#def collect(link(
    #grab first chapter link
    #grab content
        #append to array(?)
    #check for next chapter link
        #grab link
            #collect(link)
        #if last
            #make pdf and save
