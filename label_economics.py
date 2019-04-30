import datetime as dt

def months_between(date1,date2):
    if date1>date2:
        date1,date2=date2,date1
    m1=date1.year*12+date1.month
    m2=date2.year*12+date2.month
    months=m2-m1
    if date1.day>date2.day:
        months-=1
    elif date1.day==date2.day:
        seconds1=date1.hour*3600+date1.minute+date1.second
        seconds2=date2.hour*3600+date2.minute+date2.second
        if seconds1>seconds2:
            months-=1
    return months+1

import pandas as pd
import sqlite3
from dateutil import relativedelta

def update_months_since_1800_Jan():
    ref_point=dt.datetime.strptime('01Jan1800', '%d%b%Y')
    conn=sqlite3.connect('SONGS.db')
    cur=conn.cursor()
    needs_update=cur.execute("select PK, YearDate from song where jan1800 is null").fetchall()
    print(len(needs_update))
    for i in needs_update:
        DATE_DB=i[1]
        date_point=dt.datetime.strptime(DATE_DB, '%B %d %Y')
        mo=months_between(date_point, ref_point)
        cur.execute("UPDATE SONG SET jan1800=? WHERE PK =?",(mo,i[0]))
        conn.commit()

def update_economics():
    conn=sqlite3.connect('SONGS.db')
    cur=conn.cursor()
    nber=pd.read_excel('NBER chronology.xlsx',header=2,usecols='E:F',nrows=34)
    boom=sorted(nber['Peak month number'].dropna().tolist())
    bust=sorted(nber['Trough month number'].dropna().tolist())
    for i in cur.execute("select PK,jan1800 from song where economic is null").fetchall():
        pk,target=i
        abs_boom=[abs(i-target) for i in boom]
        abs_bust=[abs(i-target) for i in bust]
        cloest_boom=boom[abs_boom.index(min(abs_boom))]
        cloest_bust=bust[abs_bust.index(min(abs_bust))]
        distance_boom=abs(target-cloest_boom)
        distance_bust=abs(target-cloest_bust)
        if distance_boom<=distance_bust:
            cur.execute("UPDATE SONG SET economic=1 WHERE PK =?",(pk,))
            conn.commit()
        else:
            cur.execute("UPDATE SONG SET economic=0 WHERE PK =?",(pk,))
            conn.commit()
