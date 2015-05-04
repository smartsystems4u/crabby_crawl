# Simple spider based on Scrapy framwework
#
import sqlite3 as lite
import datetime, time
from scrapy.contrib.loader import ItemLoader
from scrapy import Spider, Item, Field
from scrapy.mail import MailSender
from scrapy.utils.project import get_project_settings

mailer = MailSender(smtphost="smtp.gmail.com", mailfrom="crawler", smtpuser="wvandoesburg@gmail.com",
smtppass="\"Y7RS/cX1$&Admq:q#'X6V!k,", smtpport=465, smtptls=True, smtpssl=True)

#TODO: put this input in a config file
#productsearchlist = ['dremel', 'fpga', 'pcb mill']
#base_urls = ['http://www.marktplaats.nl/z.html?query=',
#             'http://www.ebay.nl/sch/i.html?_nkw=']
#marktplaats_description_xpath = "//span[@class='mp-listing-title']/@title"
#marktplaats_price_xpath = "//div[@class='price-new ellipsis']/text()"
#marktplaats_date_xpath="//div[@class='date']/text()"
#marktplaats_url_xpath="//a[@class='juiceless-link description']/@href"
#marktplaats_url_xpath="//h2/a/@href"


class Product(Item):
    description = Field()
    url = Field()
    price = Field()
    date_posted = Field()
    hashtag = Field()

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


    def mail_results(self, url, items):
        mailer.send(to='wvandoesburg@gmail.com', subject='crawler results: ' +
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + url, body=str(items) )

#this parser is marktplaats specific, TODO; generalize this code so we can call specific parsers for each start_url
#this parser retrieves items, next step is to select only items of interest
    def parse(self, response):
        #check which urls match the reponse url (contains)
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
            if date_posted_xpath is not None:
                returnitem['date_posted'] = sel.select("." + date_posted_xpath).extract()[0].strip()

            items.append(returnitem)
#        if len(items) > 0:
#            self.mail_results(response.url, items)
        db_con.close()
        return items
