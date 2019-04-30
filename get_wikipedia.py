import pandas as pd
from lxml import html
import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
import codecs
import os
#table2d comes from here https://stackoverflow.com/questions/48393253/how-to-parse-table-with-rowspan-and-colspan/48451104
scrape_main_page=False
parse_top100=False
conn=sqlite3.connect('SONGS.db')
cur=conn.cursor()
parse_top_singes=True
if scrape_main_page==True:
    #List of Billboard top-ten singles
    page = requests.get('https://en.wikipedia.org/wiki/List_of_Billboard_top-ten_singles')
    webpage = html.fromstring(page.content)
    urls=sorted(['https://en.wikipedia.org'+i for i in set(webpage.xpath('//a/@href')) if '/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_' in i])
    for url in urls:
        try:
            cur.execute("INSERT INTO Wiki (Url,Note) Values (?,?)",(url,'List of Billboard top-ten singles'))
            conn.commit()
        except:
            pass
    #List of Billboard number-one singles
    page = requests.get('https://en.wikipedia.org/wiki/List_of_Billboard_number-one_singles')
    webpage = html.fromstring(page.content)
    urls=sorted(['https://en.wikipedia.org'+i for i in set(webpage.xpath('//a/@href')) if ('/wiki/List_of_Billboard_Hot_100_number-one_singles_of_' in i or
                 'List_of_Billboard_number-one_singles_of_' in i) and 'List_of_Billboard_Hot_100_number-one_singles_of_the_' not in i and 'List_of_Billboard_number-one_singles_of_the_' not in i
                 and '#Hot_100' not in i])
    for url in urls:
        try:
            cur.execute("INSERT INTO Wiki (Url,Note) Values (?,?)",(url,'List of Billboard number-one singles'))
            conn.commit()
        except:
            pass
from itertools import product

def table_to_2d(table_tag):
    rowspans = []  # track pending rowspans
    rows = table_tag.find_all('tr')

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1.
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere.
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom.
        try:
            rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        except:
            rowspans += [1 or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            try:
                rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            except:
                rowspan = rowspans[col] = 1 or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1
            value = cell.get_text()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value.replace('\n','')
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table
def parse_h100top10(url):
    # this code written in beautifulsoup python3.5
    # fetch one wikitable in html format with links from wikipedia

    fullTable = '<table class="wikitable">'

    rPage = requests.get(url)
    soup = BeautifulSoup(rPage.content, "lxml")

    table = soup.find_all("table", {"class": "wikitable"})[0]
    aa=table_to_2d(table)
    df = pd.DataFrame(aa[1:], columns=aa[0])
    return df

if parse_top100==True:
    urls=[i[0] for i in cur.execute("SELECT Url from Wiki where URL not like '%https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_%'").fetchall()]

    for url in urls:
        try:
            df=parse_h100top10(url)
            for ix,row in df.iterrows():
                if 'Singles from ' in row['Top tenentry date']:
                    year=row['Top tenentry date'][-4:]
                    continue
                title=row['Single'].replace('"','')
                try:
                    artist=row['Artist(s)']
                except:
                    artist=row['Artist']
                date=row['Top tenentry date']+' '+year
                try:
                    cur.execute("INSERT INTO SONG VALUES(?,?,?,?,?,?,?,?)",(title+artist+date+url,title,artist,url,None,year,row['Top tenentry date'],date))
                    conn.commit()
                except Exception as ex:
                    print(ex,url)
        except Exception as ex:
            print(ex,url)

if parse_top_singes==True:
    urls=[i[0] for i in cur.execute("SELECT Url from Wiki where URL like '%https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_%' or URL like '%https://en.wikipedia.org/wiki/List_of_Billboard_number-one_singles_of_%'").fetchall()]
    for url in urls:
        print(url)
        try:
            df=parse_h100top10(url)
            for ix,row in df.iterrows():
                year=url[-4:]
                title=row['Song'].replace('"','')
                try:
                    artist=row['Artist(s)']
                except:
                    artist=row['Artist']
                date=row['Issue date']+' '+year
                try:
                    cur.execute("INSERT INTO SONG VALUES(?,?,?,?,?,?,?,?)",(title+artist+date+url,title,artist,url,None,year,row['Issue date'],date))
                    conn.commit()
                except Exception as ex:
                    print(ex,url)
        except Exception as ex:
            print(ex)
