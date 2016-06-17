# -*- coding: utf-8 -*-
import re
from datetime import datetime
import String
import bs4
import MyImage
import config
import cStringIO
import urllib
from PIL import Image
import os

def get_meta_description(soup):
    meta = soup.find_all("meta", attrs={"name": "description"})
    if len(meta):
        meta_content = meta[0]['content']
        meta_content = re.sub(' - VnExpress', '', meta_content)
        return meta_content

def get_seo_url(soup):
    title = soup.find('title')
    news_title = String.bo_dau(title.get_text()).strip()
    news_title = news_title.lower()
    news_title = re.sub('vnexpress', '', news_title)
    news_title = re.sub(r'[^a-zA-Z0-9]', '-', news_title)
    news_title = re.sub(r'-+', '-', news_title)
    news_title = re.sub(r'(^-+|-+$)', '', news_title)
    return news_title

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

def get_article_content(news_content, title_content):
    content = ''
    p_list = []
    news_content = news_content.select('.fck_detail')

    if (not(news_content) or not(len(news_content))):
        return False

    news_content = news_content[0]
    img_count = 0
    attachment_data = []
    post_img_data = []
    _today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for child in news_content.children:
        if (not(type(child) == bs4.element.Tag)):
            continue

        if (child.name == 'p'):
            p_list.append("<p>"+child.get_text()+"</p>")

        if (child.name == 'table' and 'class' in child.attrs and 'tplCaption' in child['class']):
            table_img_list = child.select('img')

            if (not(len(child.select('img')))):
                continue

            table_img = table_img_list[0]
            img_src = table_img['src']

            table_caption_list = child.select('p.Image')

            if (not(table_caption_list) or not(len(table_caption_list))):
                caption = title_content
            else:
                # sometime there are more than 1 p.Image, so loop through all tag to find the caption
                for img_ in table_caption_list:
                    table_caption = img_

                    break_ = False
                    if (type(table_caption).__name__ == 'unicode'):
                        break_ = True

                    tmp = table_caption.get_text()

                    if ( not( type(tmp).__name__ in ['unicode', 'str'] )
                        or not(tmp)
                        or not(len(tmp))
                        ):
                        caption = title_content
                    else:
                        caption = table_caption.get_text().strip()

                    if (break_): break

            img_name = String.slug(caption)
            img_name = String.subif(img_name, 64)
            img_count = img_count + 1

            _post_img_data = create_thumbnail(img_src, img_name, str(img_count))

            _attachment_data = {
                'post_date': _today,
                'article_content': caption,
                'title_content': caption,
                'meta_content': caption,
                'seo_url': img_name+'_'+str(img_count),
                'post_img_data': _post_img_data,
            }
            attachment_data.append(_attachment_data)

            fucking_width = 500 if _post_img_data['width'] > 500 else _post_img_data['width']

            alt = String.subif(caption, 64)

            img = u'[caption id="" align="aligncenter" width="{}"] \
                <img class="" src="{}{}" \
                alt="{}" title="{}" \
                width="{}" /> {}[/caption]'.format(
                fucking_width,
                config.UPLOAD_PATH,
                _post_img_data['file'],
                alt,
                alt,
                fucking_width,
                caption
            )

            p_list.append(img)

    p_list.append("<p><em>Theo VnExpress<em></p>")

    if len(p_list):
        content = content.join( p_list )

    return (content, attachment_data)

def get_datetime(news_content):
    post_time = news_content.select('.block_timer')[0].get_text()
    post_time_arr = post_time.split('|')
    date_str = post_time_arr[0].strip().split(',')[1].strip()
    time_str = post_time_arr[1].strip()
    return datetime.strptime(date_str+','+time_str, "%d/%m/%Y,%H:%M GMT+7")

def create_thumbnail(url, name, img_count):
    if (len(name) > 64):
        name = name[0:64]

    name = name + '_' + img_count

    file = cStringIO.StringIO(urllib.urlopen(url).read())
    data = {}
    im = Image.open(file)
    im_ext = im.tile[0][0]
    im_format = im.format

    if im_ext == "zip":
        im_ext = 'png'

    today = datetime.today()
    today_dir = "{}/{}/{}/".format(str(today.year).zfill(4), str(today.month).zfill(2), str(today.day).zfill(2))
    today_path = "{}/{}/{}/".format(str(today.year).zfill(4), str(today.month).zfill(2), str(today.day).zfill(2))

    if (not(os.path.isdir(config.UPLOAD_DIR+today_dir))):
        os.makedirs(config.UPLOAD_DIR+today_dir, 0777)

    width, height = im.size
    data["width"] = width
    data["height"] = height
    data["file"] = today_path + name + "."+im_ext

    im.save(config.UPLOAD_DIR+today_dir+name + "."+im_ext, im_format)

    data["size"] = {}
    data["image_meta"] = {
        "aperture":0,
        "credit":"",
        "camera":"",
        "caption": name,
        "created_timestamp":0,
        "copyright":"",
        "focal_length":0,
        "iso":0,
        "shutter_speed":0,
        "title": name,
        "orientation":0,
        "keywords":[
            name
        ]
    }

    fucking_size = {
        "thumbnail":{
            "width":150,
            "height":150
        },
        "medium":{
            "width":300,
            "height":222
        },
        "blog-post-thumb-big":{
            "width":510,
            "height":374
        },
        "blog-post-thumb":{
            "width":330,
            "height":242
        },
        "blog-post-thumb-medium":{
            "width":510,
            "height":187
        },
        "post-grid-thumb-big":{
            "width":524,
            "height":444
        },
        "post-grid-thumb-medium":{
            "width":524,
            "height":261
        },
        "pressroom-gallery-thumb-type-3":{
            "width":130,
            "height":95
        },
        "pressroom-small-thumb":{
            "width":100,
            "height":100
        }
    }

    if im_ext == "gif":
        return data

    for siz in fucking_size:
        _size = fucking_size[siz]['width'], fucking_size[siz]['height']
        file = cStringIO.StringIO(urllib.urlopen(url).read())
        _suffix = ("-{}x{}.{}").format(_size[0], _size[1], im_ext)
        file_path = str(config.UPLOAD_DIR+today_dir+name) + _suffix
        file_name = name + _suffix

        MyImage.resize_and_crop(file, file_path, _size, im_format, 'middle')

        data["size"][siz] = {
            "file": file_name,
            "width": _size[0],
            "height": _size[1],
            "mime-type":"image/"+im_format.lower()
        }

    return data