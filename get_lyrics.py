import requests
import sqlite3
import re
from bs4 import BeautifulSoup
from unidecode import unidecode
import se
import json
import base64
import time
conn=sqlite3.connect('SONGS.db')
cur=conn.cursor()

target=set([i for i in cur.execute("select year,Title,artist from song where allurl is null").fetchall()])
base='http://www.songlyrics.com/index.php?section=search&searchW={}&submit=Search'
scrape_website=False

if scrape_website==True:
    for i in target:
        query=i[-1]+' '+i[-2]
        query=unidecode(query)
        query = re.sub('[^0-9a-zA-Z()\"\'_\-.\?\!]+', ' ', query)
        query ='+'.join(query.split())
        url=base.format(query)
        #html=se.getsource(url)
        html=requests.get(url).content
        html=BeautifulSoup(html,'lxml')
        try:
            lyric_url=html.find('div',attrs={'class':'serpresult'}).find('a',attrs={'href':True})['href']
            lyric_url_pack= bytes(json.dumps([i['href'] for i in html.find_all('a',attrs={'href':True})]),'utf-8')
            lyric_url_pack = base64.b64encode(lyric_url_pack)
            try:
                cur.execute("UPDATE SONG SET AllURL=?,Lyricsdotcom=? WHERE YEAR=? and TITLE=? and ARTIST=?",(lyric_url_pack,lyric_url,i[0],i[1],i[2]))
                conn.commit()
            except Exception as ex:
                print(ex)
        except Exception as ex:
            print(ex)


target=set([i for i in cur.execute("select Lyricsdotcom,Year,Title,Artist from song where lyrics is null").fetchall()])
for i in target:
    time.sleep(3)
    url,year,title,artist=i
    #html=se.getsource(url)
    try:
        html=requests.get(url).content
        html=BeautifulSoup(html,'lxml')
        print(url)
        title_ly=html.find('div',attrs={'class':'pagetitle'}).find('h1').text
        artist_ly=html.find('div',attrs={'class':'pagetitle'}).find('p').text
        lyrics=html.find('p',attrs={'id':'songLyricsDiv'}).text
        try:
            print(title_ly,artist_ly,lyrics)
            cur.execute("UPDATE SONG SET Lyrics=?,TitleLyricsdotcom=?,ArtistLyricsdotcom=? WHERE YEAR=? and TITLE=? and ARTIST=?",(lyrics,title_ly,artist_ly,year,title,artist))
            conn.commit()
        except Exception as ex:
            print(ex)
    except Exception as ex:
        print(ex)
