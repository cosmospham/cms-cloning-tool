# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz
import urllib
import Vne

def get_content(link):
    data = {}

    # try:
    content = urllib.urlopen(link).read()
    news_content_soup = BeautifulSoup(content, "lxml")

    # remove all script tags in news_content_soup
    [x.extract() for x in news_content_soup.findAll("script")]

    news_content_list = news_content_soup.select(".block_col_480")
    if len(news_content_list) == 0:
        return data

    local = pytz.timezone("Asia/Ho_Chi_Minh")

    news_content    = news_content_list[0]
    seo_url         = Vne.get_seo_url(news_content_soup)
    title_content   = Vne.get_article_title(news_content)
    meta_content    = Vne.get_meta_description(news_content_soup)
    date_obj        = Vne.get_datetime(news_content)
    post_content    = Vne.get_article_content(news_content, title_content)
    category_slug   = Vne.get_category(link)
    post_id         = Vne.get_post_id(link)

    local_dt        = local.localize(date_obj, is_dst=None)
    utc_dt          = local_dt.astimezone(pytz.utc)

    article_content = post_content[0]
    attachment_data = post_content[1]

    if (not(title_content) or not(len(article_content))):
        return False

    data = {
        'seo_url': seo_url,
        'title_content': title_content,
        'meta_content': meta_content,
        'date_obj': date_obj,
        'article_content': article_content,
        'post_date': local_dt.strftime("%Y-%m-%d %H:%M:%S"),
        'post_date_gmt': utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        'post_modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'post_modified_gmt': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        'post_id': post_id,
        'category_slug': category_slug,
        'attachment_data': attachment_data
    }
    # except Exception, e:
    #     raise e

    return data

def _get_post_url(link, selector):
    url_list = []

    category_page_content = urllib.urlopen( link ).read()
    soup = BeautifulSoup(category_page_content, "lxml")

    title_news = soup.select( selector )

    for title in title_news:
        text = title.get_text()
        if (type(text) is unicode and len(text) and len(title['href'])):
            url_list.append( title['href'] )

    return url_list

def get_post_url_from_list_news(link):
    """
    Phần danh sách bài mới ở dưới trang chủ đề
    """
    return _get_post_url(link, ".list_news .title_news a.txt_link")

def get_post_url_from_box_news_top(link):
    """
    Phần trên trang chủ đề
    """
    return _get_post_url(link, "#box_news_top .title_news a.txt_link")

def get_post_url_in_category(link):
    post_url_list = []
    post_url_list = post_url_list + get_post_url_from_box_news_top(link)
    post_url_list = post_url_list + get_post_url_from_list_news(link)
    return post_url_list

def get_category_list():
    """
    Get list of category from the menu
    """
    category_list = {}

    home_page_content = urllib.urlopen("http://vnexpress.net/").read()
    soup = BeautifulSoup(home_page_content, "lxml")

    title_news = soup.select("#menu_web li a")

    for title in title_news:
        text = title.get_text()
        if (type(text) is unicode and len(text)):
            url = title['href']

            if ( not( re.search('(vnexpress.net)', url) ) ):
                url = 'http://vnexpress.net' + url

            category_list[ url ] = text

    return category_list
