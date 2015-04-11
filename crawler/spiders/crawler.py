# Simple spider based on Scrapy framwework
#
import datetime, time
from scrapy.contrib.loader import ItemLoader
from scrapy import Spider, Item, Field
from scrapy.mail import MailSender

mailer = MailSender(smtphost="smtp.gmail.com", mailfrom="crawler", smtpuser="wvandoesburg@gmail.com",
smtppass="\"Y7RS/cX1$&Admq:q#'X6V!k,", smtpport=465, smtptls=True, smtpssl=True)

#TODO: put this input in a config file
productsearchlist = ['dremel', 'fpga', 'pcb mill']
base_urls = ['http://www.marktplaats.nl/z.html?query=',
             'http://www.ebay.nl/sch/i.html?_nkw=']
marktplaats_description_xpath = "//span[@class='mp-listing-title']/@title"
marktplaats_price_xpath = "//div[@class='price-new ellipsis']/text()"
marktplaats_date_xpath="//div[@class='date']/text()"
#marktplaats_url_xpath="//a[@class='juiceless-link description']/@href"
marktplaats_url_xpath="//h2/a/@href"


class Product(Item):
    description = Field()
    url = Field()
    price = Field()
    date_posted = Field()
    hashtag = Field()

class ProductSpider(Spider):
    name = 'productspider'
    start_urls = []
    for site in base_urls:
        for product in productsearchlist:
            start_urls.append( site + product )

    def mail_results(self, url, items):
        mailer.send(to="wvandoesburg@gmail.com", subject='crawler results: ' +
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + url, body=str(items) )

#this parser is marktplaats specific, TODO; generalize this code so we can call specific parsers for each start_url
#this parser retrieves items, next step is to select only items of interest
    def parse(self, response):
        sub_selectors = response.xpath('//article')
        items = []
        for sel in sub_selectors:
            returnitem = Product()
            returnitem['description'] = sel.select("." + marktplaats_description_xpath).extract()
            returnitem['price'] = sel.select("." + marktplaats_price_xpath).extract()[0].encode('ascii',
                    errors='ignore').strip()
            returnitem['url'] = sel.select("." + marktplaats_url_xpath).extract()
            returnitem['date_posted'] = sel.select("." + marktplaats_date_xpath).extract()[0].strip()
            items.append(returnitem)
#        if len(items) > 0:
#            self.mail_results(response.url, items)
        return items
