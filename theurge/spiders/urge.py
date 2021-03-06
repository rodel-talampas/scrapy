from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.utils.log import configure_logging

from theurge.items import RetailItem
import sys
import yaml
import os
import logging
from theurge.spiders.spider import Keeper

from scrapy.utils.project import get_project_settings


class UrgeSpider(CrawlSpider, Keeper):
    name = 'urge'
    test = 'rodel'
    allowed_domains = ['theurge.com']
    start_urls = ['https://theurge.com']
    settings = get_project_settings()
    total_item_to_extract = settings.getint('TOTAL_ITEMCOUNT', 300)
    total_items = 0

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    # Load the YAML Configuration
    dir_path = os.path.dirname(os.path.realpath(__file__))
    global config
    with open(r'%s/spider.yaml' % dir_path) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

    # Create Log Files
    LOG_FILE = 'logs/spider.log'
    ERR_FILE = 'logs/spider_error.log'
    configure_logging(install_root_handler=False)
    logging.basicConfig(level=logging.INFO, filemode='w+', filename=LOG_FILE)
    logging.basicConfig(level=logging.ERROR, filemode='w+', filename=ERR_FILE)


    # This method parses the item per extract in the page
    # The original code uses hardcoded css and xpath
    # e.g.
    #   item['title'] = selector.css("h1._31Nwh.JLwaS::text").get()
    #   item['price'] = selector.css('div.eP0wn._2xJnS span._2plVT::text').get()
    #   item['brand'] = selector.css("span.URfXD::text").get()
    #   item['salePrice'] = selector.xpath("//*[@class='_2Mqpk']/a[1]/div[2]/text()[2]").get()
    #   item['description'] = selector.xpath("//article/a/p/text()").get()       
    #
    # This method has been revised to used a yaml configuration as per loaded above
    def parse_item(self, response): 
        selector = Selector(response)

        item = RetailItem()
        # Retrieve 'urge' spider configuration
        urge_items = [ items for key, items in config.items() if key == self.name ][0] 
        css_items = [ urge_items[key] for key in urge_items if key == 'css' ][0]
        xpath_items = [ urge_items[key] for key in urge_items if key == 'xpath' ][0]

        for key in css_items:
            item[key] = selector.css(css_items[key]).get()

        for key in xpath_items:
            item[key] = selector.xpath(xpath_items[key]).get()

        # call house keeping method
        self.add_keeper_info(item,response)
        return item
