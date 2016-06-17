# -*- coding: utf-8 -*-
import pymysql
import String
import os
import traceback
import sys
from datetime import datetime
from phpserialize import *

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = pymysql.connect(host=config.HOST, user=config.USER_NAME, passwd=config.PASSWORD, db=config.DB_NAME,
                                    autocommit=False, charset="utf8")

    def commit(self):
        self.conn.commit()

    def begin(self):
        self.conn.begin()

    def close(self):
        self.conn.close()

    def fetchone(self, sql, data):
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, data)
                return cur.fetchone()
        except Exception, e:
            print(traceback.format_exc())
            return False

    def execute(self, sql, data):
        try:
            with self.conn.cursor() as cur:
                return cur.execute(sql, data)
        except Exception, e:
            print(traceback.format_exc())
            return False

    def post_exists(self, post_id):
        sql = "SELECT meta_id FROM "+self.config.TABLE_PREFIX + 'postmeta'+" WHERE meta_key LIKE 'vnexpress_id' AND meta_value LIKE %s"
        return True if self.fetchone(sql, (post_id)) else False

    def insert_post_data(self, data):
        try:
            with self.conn.cursor() as cur:
                sql = "INSERT INTO "+self.config.TABLE_PREFIX+'posts'+"( \
                        post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, \
                        comment_status, ping_status, post_name, post_modified, post_modified_gmt, post_type, \
                        post_content_filtered, pinged, to_ping) \
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                cur.execute(sql, (
                    1,
                    data['post_date'],
                    data['post_date_gmt'],
                    data['article_content'],
                    data['title_content'],
                    data['meta_content'],
                    'publish',
                    'open',
                    'open',
                    data['seo_url'],
                    data['post_modified'],
                    data['post_modified_gmt'],
                    'post',
                    '', '', ''
                ))

                id = cur.lastrowid

                if (id):
                    # meta for main post
                    sql = "INSERT INTO "+self.config.TABLE_PREFIX+'postmeta'+"(post_id, meta_key, meta_value) \
                            VALUES(%s, %s, %s)"
                    cur.execute(sql, (id, 'vnexpress_id', data['post_id']))

                    if ('attachment_data' in data):
                        set_thumbnail = True
                        attachment_data = data['attachment_data']
                        for att in attachment_data:
                            self.insert_attachment(att, id, set_thumbnail)
                            if (set_thumbnail):
                                set_thumbnail = False


                return id
        except Exception, e:
            print(traceback.format_exc())

    def insert_attachment(self, data, parent, set_thumbnail=False):
        # insert attachment
        with self.conn.cursor() as cur:
            sql = "INSERT INTO "+self.config.TABLE_PREFIX+'posts'+"( \
                    post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, \
                    comment_status, ping_status, post_name, post_modified, post_type, post_parent, post_mime_type, \
                    post_content_filtered, pinged, to_ping) \
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            cur.execute(sql, (
                1,
                data['post_date'],
                data['post_date'],
                data['article_content'],
                data['title_content'],
                data['meta_content'],
                'inherit',
                'open',
                'closed',
                data['seo_url'],
                data['post_date'],
                'attachment',
                parent,
                'image/jpeg',
                '', '', ''
            ))

            post_id = cur.lastrowid

            if ('post_img_data' in data):
                meta = data['post_img_data']

                # meta for attachment
                sql = "INSERT INTO "+self.config.TABLE_PREFIX+'postmeta'+"( \
                    post_id, meta_key, meta_value) VALUES \
                    (%s, %s, %s),\
                    (%s, %s, %s),\
                    (%s, %s, %s)"
                cur.execute(sql,
                    (post_id, '_wp_attached_file', meta['file'],
                     post_id, '_wp_attachment_metadata', dumps(meta),
                     post_id, '_wp_attachment_image_alt', data['meta_content']
                ))

            if (set_thumbnail):
                sql = "INSERT INTO "+self.config.TABLE_PREFIX+'postmeta'+"( \
                    post_id, meta_key, meta_value) VALUES \
                    (%s, %s, %s)"
                cur.execute(sql,
                    (parent, '_thumbnail_id', post_id,
                ))

    def insert_post(self, data):
        try:
            if (data and not( self.post_exists(data['post_id']) ) ):
                return self.insert_post_data(data)
        except Exception, e:
            print(traceback.format_exc())

    def get_category_id(self, name):
        sql = "SELECT t.term_id, tt.term_taxonomy_id FROM "+self.config.TABLE_PREFIX + 'terms t'+"\
            JOIN "+self.config.TABLE_PREFIX+"term_taxonomy tt ON t.term_id=tt.term_id WHERE tt.taxonomy LIKE 'category' AND t.name LIKE %s"
        return self.fetchone(sql, (name))

    def insert_category(self, name): #ok
        category = self.get_category_id(name)
        if (not(category) or not(category[0])):
            with self.conn as cur:
                sql = "INSERT INTO " + self.config.TABLE_PREFIX + "terms (name, slug) VALUES (%s, %s)"
                cur.execute(sql, (name, String.slug(name)))
                category_id = cur.lastrowid

                sql = "INSERT INTO " + self.config.TABLE_PREFIX + "term_taxonomy (term_id, taxonomy, description) VALUES (%s, 'category', %s)"
                cur.execute(sql, (category_id, name))
                term_taxonomy_id = cur.lastrowid
        else:
            term_taxonomy_id = category[1]

        return term_taxonomy_id

    def insert_relationships(self, post_id, category_id):
        print post_id, category_id
        if (not(post_id) or not(category_id)):
            return False

        with self.conn as cur:
            sql = "REPLACE INTO " +self.config.TABLE_PREFIX+"term_relationships (object_id, term_taxonomy_id) VALUES(%s, %s)"
            cur.execute(sql, (post_id, category_id))
            term_taxonomy_id = cur.lastrowid

            if (term_taxonomy_id):
                sql = "UPDATE " + self.config.TABLE_PREFIX + "term_taxonomy SET count = count + 1 WHERE term_taxonomy_id = %s"
                cur.execute(sql, (term_taxonomy_id))
            return True