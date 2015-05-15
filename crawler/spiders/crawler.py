# Simple spider based on Scrapy framwework
#
import sqlite3 as lite
import datetime, time
from scrapy.contrib.loader import ItemLoader
from scrapy import Spider, Item, Field
from scrapy.mail import MailSender
from scrapy.utils.project import get_project_settings

#Enter your mail settings below!
mailer = MailSender(smtphost="<your smtp server>", mailfrom="crawler", smtpuser="<your email username>",
smtppass="<your email passwd>", smtpport=465, smtptls=True, smtpssl=True)

class Product(Item):
    description = Field()
    url = Field()
    price = Field()
    date_posted = Field()
    hashtag = Field()
    objective_id = Field()
    url_id = Field()

class ProductSpider(Spider):
    name = 'productspider'
    settings = get_project_settings()
    
    db_con = lite.connect(settings.get('DB'))
    db_con.row_factory = lite.Row
    #c = db_con.cursor()
    
    start_urls = []
    for site in db_con.execute("select url from url"):
        for product in db_con.execute("select search_terms from objective"):
            start_urls.append( site["url"] + product["search_terms"] )
            print 'added: ' + site["url"] + product["search_terms"] 
    db_con.close()

# Enter the mail recipient to which you want to mail the results!
    def mail_results(self, url, items):
        mailer.send(to='<mail recipient here>', subject='crawler results: ' +
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + url, body=str(items) )

    def parse(self, response):
        #check which urls match the response url (contains)
        #get parsers for matching url
        db_con = lite.connect(self.settings.get('DB'))
        db_con.row_factory = lite.Row

        url_id = 0
        for url in db_con.execute("select * from url"):
            if url["url"] in response.url:
                url_id = url["id"]
       
        if url_id == 0:
            raise AssertionError('No valid URL found')

        cur = db_con.execute("select * from Parser where url = ?", str(url_id))
        parser = cur.fetchone()

        search_terms = response.url.rpartition('=')[2]
        print 'terms: ' + search_terms
        cur = db_con.execute("select * from objective where search_terms = ?", (search_terms,))
        objective_id = cur.fetchone()["id"]

        description_xpath = parser["description"]
        price_xpath = parser["price"]
        url_xpath = parser["item_url"]
        date_posted_xpath = parser["date_posted"]
        subselector = parser["subselector"]
        

# determine if a sub selector is necessary
        sub_selectors = response.xpath(subselector)
        items = []
        for sel in sub_selectors:
            returnitem = Product()
            returnitem['description'] = sel.select( "." + description_xpath).extract()
            returnitem['price'] = ''.join(sel.select("." + price_xpath).extract()).encode('ascii', errors='ignore').strip()
            returnitem['url'] = sel.select("." + url_xpath).extract()
            returnitem['url_id'] = int(url_id)
            returnitem['objective_id'] = int(objective_id)
            if date_posted_xpath is not None:
                returnitem['date_posted'] = sel.select("." + date_posted_xpath).extract()[0].strip()
            else:
                returnitem['date_posted'] = ""

            items.append(returnitem)
        if len(items) > 0:
            self.mail_results(response.url, items)
        db_con.close()
        return items
