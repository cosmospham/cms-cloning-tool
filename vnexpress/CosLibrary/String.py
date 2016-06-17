# -*- coding: utf-8 -*-
import re

def bo_dau(str):
    try:
        if str == '': return

        decode = False
        if type(str).__name__ == 'unicode':
            decode = True
            str = str.encode('utf-8')

        list_pat = ["á|à|ả|ạ|ã|â|ấ|ầ|ẩ|ậ|ẫ|ă|ắ|ằ|ẳ|ặ|ẵ", "Á|À|Ả|Ạ|Ã|Â|Ấ|Ầ|Ẩ|Ậ|Ẫ|Ă|Ắ|Ằ|Ẳ|Ặ|Ẵ",
                    "đ", "Đ", "í|ì|ỉ|ị|ĩ", "Í|Ì|Ỉ|Ị|Ĩ", "é|è|ẻ|ẹ|ẽ|ê|ế|ề|ể|ệ|ễ", "É|È|Ẻ|Ẹ|Ẽ|Ê|Ế|Ề|Ể|Ệ|Ễ",
                    "ó|ò|ỏ|ọ|õ|ô|ố|ồ|ổ|ộ|ỗ|ơ|ớ|ờ|ở|ợ|ỡ", "Ó|Ò|Ỏ|Ọ|Õ|Ô|Ố|Ồ|Ổ|Ộ|Ỗ|Ơ|Ớ|Ờ|Ở|Ợ|Ỡ",
                    "ú|ù|ủ|ụ|ũ|ư|ứ|ừ|ử|ự|ữ", "Ú|Ù|Ủ|Ụ|Ũ|Ư|Ứ|Ừ|Ử|Ự|Ữ", "ý|ỳ|ỷ|ỵ|ỹ", "Ý|Ỳ|Ỷ|Ỵ|Ỹ"]
        list_re = ['a', 'A', 'd', 'D', 'i', 'I', 'e', 'E', 'o', 'O', 'u', 'U', 'y', 'Y']
        for i in range(len(list_pat)):
            str = re.sub(list_pat[i], list_re[i], str)

        if (decode): str = str.decode('utf-8')

        return str
    except:
        traceback.print_exc()

def slug(str):
    if (not(str) or not(len(str))):
        return ''

    slug = bo_dau(str).strip()
    slug = slug.lower()
    slug = re.sub(r'[^a-zA-Z0-9]', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = re.sub(r'(^-+|-+$)', '', slug)
    return slug

def subif(str, length):
    if str == '': return
    res_str = str
    if (len(str) > length): res_str = str[0:length]
    return res_str

