# -*- coding: utf-8 -*-
from CosLibrary import config
from CosLibrary.Database import Database
from CosLibrary import Content
from CosLibrary import Vne
import os

def main():
    count = 0

    category_links = Content.get_category_list()
    db = Database(config)

    for category_link in category_links:
        db.begin()
        term_taxonomy_id = db.insert_category(category_links[category_link])
        db.commit()

        # quét từng category
        post_url_in_category = Content.get_post_url_in_category( category_link )
        # post_url_in_category = ["http://dulich.vnexpress.net/tin-tuc/cong-dong/hoi-dap/doan-ten-nuoc-qua-quoc-ky-3379112.html"]

        for url in post_url_in_category:
            print url
            db.begin()
            post_id = False
            _tmp_id = Vne.get_post_id(url)

            if (db.post_exists(_tmp_id)):
                continue

            data = Content.get_content(url)
            post_id = db.insert_post(data)
            if (post_id):
                db.insert_relationships(post_id, term_taxonomy_id)
                count = count + 1
                print "count: "+str(count)
                # break
            else:
                print "no insert"
            db.commit()
            print "---"
            # break
        # break

    db.close()
    print "Total " + str(count) + " inserted"

main()
