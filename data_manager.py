# -*- coding: utf-8 -*-

import psycopg2
import sys
import requests
from bs4 import BeautifulSoup

header = {
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    'Host': "book.douban.com"
    }


con = None

try:
     
    con = psycopg2.connect("dbname='librarydb' user='dbuser' host='127.0.0.1' password='dbuser'") 
    cur = con.cursor()
    for i in range(10):
        url = "http://book.douban.com/top250?start=" + str(i * 25)
        r = requests.get(url, headers=header)
        soup = BeautifulSoup(r.content)
        book_list = soup.find_all("div", class_="pl2")

        for j in range(len(book_list)):
            try:
                book_url = book_list[j].find("a")["href"]
                book_r = requests.get(book_url, headers=header)
                book_soup = BeautifulSoup(book_r.content)
                book_name = book_soup.find("h1").find("span").string
                info = book_soup.find("div", id="info")
                info_list = info.find_all("span", class_="pl")
                for k in range(len(info_list)):
                    if "作者" in info_list[k].string.encode("utf-8"):
                        author = info_list[k].find_next_sibling().string
                    if "出版社" in info_list[k].string.encode("utf-8"):
                        press = info_list[k].next_element.next_element.strip()
                    if "ISBN" in info_list[k].string:
                        ISBN = info_list[k].next_element.next_element.strip()
                print book_name
                print author
                print press
                print ISBN    
                cur.execute("INSERT INTO book (book_name, press, author, ISBN, amount, \
                    order_amount, borrow_amount) VALUES (%s, %s, %s, %s, 5, 0, 0)", (book_name, press, author, ISBN))
            except:
                pass
            
    con.commit()    

except psycopg2.DatabaseError, e:


    if con:
        con.rollback()

    print 'Error %s' % e    
    sys.exit(1)
    
    
finally:
    
    if con:
        con.close()

