# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


def short_url(url):
    if len(url) <= 100:
        return url
    return url[:22] + '...' + url[-78:]


class OlxscraperPipeline:
    def process_item(self, item, spider):
        return item


class SaveToPostgresqlPipeline:

    def __init__(self):
        self.conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password='postgres',
            database='rodas_com'
        )

        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        db_record = self.select_html_docs(item['url_hash'], spider)

        if db_record is None:
            self.upsert_html_doc(item, spider)
            spider.logger.debug(f'HTML inserido no banco de dados: {short_url(item["url"])}')

        elif db_record['html_hash'] != item['html_hash']:
            self.upsert_html_doc(item, spider)
            spider.logger.debug(f'HTML atualizado no banco de dados: {short_url(item["url"])}')

        else:
            spider.logger.debug(f'HTML já existe no banco de dados: {short_url(item["url"])}')

        return item

    def select_html_docs(self, url_hash, spider):
        try:
            sql = 'SELECT url_hash, html_hash FROM html_document WHERE url_hash = %s'

            self.cur.execute(sql, (url_hash,))

            response = self.cur.fetchone()
            if response is not None:
                hash_url, hash_html = response
                return {'url_hash': hash_url, 'html_hash': hash_html}
            else:
                return None

        except (Exception, psycopg2.Error) as e:
            spider.logger.error(f'Erro ao obter os documentos HTML do banco de dados.')
            raise e

    def upsert_html_doc(self, item, spider):
        try:
            sql = '''
            INSERT INTO html_document (url_hash, html_hash, category, url, html, last_visit_on, first_visit_on)
            VALUES (%(url_hash)s, %(html_hash)s, %(category)s, %(url)s, %(html)s, %(visited_on)s, %(visited_on)s)
            ON CONFLICT (url_hash) DO UPDATE
                SET html_hash     = EXCLUDED.html_hash,
                    html          = EXCLUDED.html,
                    last_visit_on = EXCLUDED.last_visit_on
            '''

            values = {
                'url_hash':   item['url_hash'],
                'html_hash':  item['html_hash'],
                'category':   item['category'],
                'url':        item['url'],
                'html':       item['html'],
                'visited_on': item['visited_on']
            }

            self.cur.execute(sql, values)
            self.conn.commit()

        except (Exception, psycopg2.Error) as e:
            spider.logger.error(f'Erro ao salvar o documento HTML no banco de dados.')
            raise e

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
        spider.logger.info(f'Conexão com o banco de dados encerrada.')
