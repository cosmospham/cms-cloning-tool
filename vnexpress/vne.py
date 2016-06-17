# -*- coding: utf-8 -*-
import urllib
from bs4 import BeautifulSoup
import codecs
import re
import traceback
from datetime import datetime
import pymysql

def bo_dau(str):
    try:
        if str == '': return
        if type(str).__name__ == 'unicode': str = str.encode('utf-8')
        list_pat = ["á|à|ả|ạ|ã|â|ấ|ầ|ẩ|ậ|ẫ|ă|ắ|ằ|ẳ|ặ|ẵ", "Á|À|Ả|Ạ|Ã|Â|Ấ|Ầ|Ẩ|Ậ|Ẫ|Ă|Ắ|Ằ|Ẳ|Ặ|Ẵ",
                    "đ", "Đ", "í|ì|ỉ|ị|ĩ", "Í|Ì|Ỉ|Ị|Ĩ", "é|è|ẻ|ẹ|ẽ|ê|ế|ề|ể|ệ|ễ", "É|È|Ẻ|Ẹ|Ẽ|Ê|Ế|Ề|Ể|Ệ|Ễ",
                    "ó|ò|ỏ|ọ|õ|ô|ố|ồ|ổ|ộ|ỗ|ơ|ớ|ờ|ở|ợ|ỡ", "Ó|Ò|Ỏ|Ọ|Õ|Ô|Ố|Ồ|Ổ|Ộ|Ỗ|Ơ|Ớ|Ờ|Ở|Ợ|Ỡ",
                    "ú|ù|ủ|ụ|ũ|ư|ứ|ừ|ử|ự|ữ", "Ú|Ù|Ủ|Ụ|Ũ|Ư|Ứ|Ừ|Ử|Ự|Ữ", "ý|ỳ|ỷ|ỵ|ỹ", "Ý|Ỳ|Ỷ|Ỵ|Ỹ"]
        list_re = ['a', 'A', 'd', 'D', 'i', 'I', 'e', 'E', 'o', 'O', 'u', 'U', 'y', 'Y']
        for i in range(len(list_pat)):
            str = re.sub(list_pat[i], list_re[i], str)
        return str
    except:
        traceback.print_exc()

def get_meta_description(soup):
    meta = soup.find_all("meta", attrs={"name": "description"})
    if len(meta):
        return meta[0]['content']

def get_seo_url(soup):
    title = soup.find('title')
    news_title = bo_dau(title.get_text()).strip()
    news_title = re.sub(r'[^a-zA-Z0-9]', '-', news_title)
    news_title = re.sub(r'-+', '-', news_title)
    news_title = re.sub(r'(^-+|-+$)', '', news_title)
    return news_title.lower()

def get_post_id(link):
    m = re.match(r'^(.*)-([0-9]+)(\.html)$', link)
    if not m:
        return []
    return m.group(2)

def get_category(link):
    m = re.match(r'^(.*)\/(.*)\/', link)
    if not m:
        return []
    return m.group(2)

def get_article_title(news_content):
    if len(news_content.select('.title_news h1')):
        return news_content.select('.title_news h1')[0].get_text()

def get_article_content(news_content):
    if len(news_content.select('.fck_detail')):
        return news_content.select('.fck_detail')[0]

def get_datetime(news_content):
    post_time = news_content.select('.block_timer')[0].get_text()
    post_time_arr = post_time.split('|')
    date_str = post_time_arr[0].strip().split(',')[1].strip()
    time_str = post_time_arr[1].strip()
    return datetime.strptime(date_str+','+time_str, "%d/%m/%Y,%H:%M GMT+7")

def get_related_post_links(soup):
    box_tinlienquan = soup.find('div', id="box_tinlienquan")
    links = []

    if box_tinlienquan:
        links = box_tinlienquan.find_all('a', {"title": True})

    return links

def get_other_post_links(soup):
    box_tinkhac_detail = soup.find('div', id="box_tinkhac_detail")
    links = []

    if box_tinkhac_detail:
        links = box_tinkhac_detail.find_all('a', {"title": True, "onclick": True})

    return links

def do_clone(link):
    global depth
    global depth_post
    global list_url
    global cur
    global post_get

    print "\n\n---------------"
    post_id = get_post_id(link)
    category = get_category(link)

    if post_id in list_url:
        print "post " + str(post_id) + " exists"
        return True

    if not depth_post[depth]:
        depth_post.insert(depth, 0)

    if depth_post[depth] >= max_post:
        print "+++++depth_post[depth] " + str(depth_post[depth]) + " / max_post: " + str(max_post)
        depth -= 1
        return False

    print "current dept: "+str(depth)
    print "depth_post: "
    print depth_post
    print "link: "+link
    print "category: " + category
    print "post_id: " + str(post_id)
    print "post_get: " + str(post_get)

    list_url.append(post_id)

    content = urllib.urlopen(link).read()
    news_content_soup = BeautifulSoup(content, "lxml")

    # remove all script tags in news_content_soup
    [x.extract() for x in news_content_soup.findAll("script")]

    news_content_list = news_content_soup.select(".block_col_480")

    if len(news_content_list) == 0:
        return True

    news_content    = news_content_list[0]
    seo_url         = get_seo_url(news_content_soup)
    title_content   = get_article_title(news_content)
    meta_content    = get_meta_description(news_content_soup)
    date_obj        = get_datetime(news_content)
    article_content = get_article_content(news_content)
    mysql_date      = date_obj.strftime("%Y-%m-%d %H:%M:00")

    depth_post[depth] += 1
    post_get += 1

    cur.execute("""INSERT INTO ttbnews_posts(post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_name, post_modified, post_type)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (1, mysql_date, mysql_date, article_content.prettify(), title_content, meta_content, 'publish', 'open', 'open', str(depth)+'-'+seo_url, mysql_date, 'post'))

    if depth >= max_depth:
        return True

    related_links = get_related_post_links(news_content_soup)
    other_links = get_other_post_links(news_content_soup)

    if related_links and len(related_links):
        depth += 1
        for x in related_links:
            if not do_clone(x['href']):
                print "related_links"
                break

    if other_links and len(other_links):
        depth += 1
        for x in other_links:
            if not do_clone(x['href']):
                print "other_links"
                break

    return True

def clone():
    global depth
    global depth_posts
    global conn
    global cur
    string = ""

    conn = pymysql.connect(host="127.0.0.1", user="root", passwd=None, db="news", autocommit=True, charset="utf8")
    cur = conn.cursor()
    list_url = []

    home_page_content = urllib.urlopen("http://vnexpress.net/").read()
    soup = BeautifulSoup(home_page_content, "lxml")

    title_news = soup.select(".title_news a.txt_link")

    for title in title_news:
        link = title['href']
        do_clone(link)

# global vars
max_depth = 20
max_post = 200
depth = 0
depth_post = [None]
post_get = 0
list_url = []
conn = False
cur = False
###
clone()