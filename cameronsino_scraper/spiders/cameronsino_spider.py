import logging
import scrapy
import time
from scrapy.contrib.spiders import CSVFeedSpider
from ..items import CameronsinoScraperItem
from selenium import webdriver
from scrapy.utils.project import get_project_settings
from config import LOGIN, PASSWORD, PHANTOMJS_PATH

logger = logging.getLogger('logger')
settings = get_project_settings()


class GameronsinoSpider(CSVFeedSpider):
    name = 'cameronsino_spider'
    start_urls = ['https://www.cameronsino.com/drop-shipping.html']
    base_url = 'https://www.cameronsino.com'
    login_url = 'https://www.cameronsino.com/dropship/dslogind.html'
    delimiter = '|'

    login_user = LOGIN
    login_password = PASSWORD

    def __init__(self, *args, **kwargs):
        super(GameronsinoSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)

    def start_requests(self):
        # let's start by sending a first request to login page
        yield scrapy.Request(self.login_url, self.login)

    def login(self, response):

        self.driver.get(url='https://www.cameronsino.com/dropship/dslogind.html')
        captcha_val = self.driver.find_element_by_xpath('//input[@id="Code"]').get_attribute('value')

        login_user = LOGIN
        login_password = PASSWORD

        username = self.driver.find_element_by_id("Username")
        password = self.driver.find_element_by_name("Password")
        captcha = self.driver.find_element_by_id("checkCode")
        username.send_keys(login_user)
        password.send_keys(login_password)
        captcha.send_keys(captcha_val)
        submit = self.driver.find_element_by_xpath('//input[@class="submit"]')
        submit.click()
        time.sleep(2)
        if 'Danawu' in self.driver.page_source:
            logging.info('Success login user: Danawu')
        else:
            logging.info('Error login')
        cookies = self.driver.get_cookies()
        # driver.close()
        for url in self.start_urls:
            # url = 'https://www.cameronsino.com/category/computer-and-data.html'
            yield scrapy.Request(url, cookies=cookies, callback=self.parse)

    def parse(self, response):
        logging.info('Parse')
        categories = response.xpath('//ul[@id="caul"]/li')
        # pdb.set_trace()
        for category in categories:
            category_name = category.xpath('./a/text()').extract_first()
            category_link = category.xpath('./a/@href').extract_first()
            print(category_name, category_link)
            # category_link = '/category/computer-and-data.html'
            # pdb.set_trace()
            yield scrapy.Request(self.base_url + category_link, callback=self.parse_category, meta={"category": category_name})

    def parse_category(self, response):
        logging.info('Parse Category')
        self.driver.get(response.url)
        time.sleep(3)
        # pdb.set_trace()
        sub_categories = response.xpath('//div[@class="BatterySeriesBody"]/a')
        images = self.driver.find_elements_by_xpath('//li[@class="BatterySeriesProductLi1"]/img')
        for sub, image in zip(sub_categories, images):
            sub_link = sub.xpath('./@href').extract_first()
            sub_name = sub.xpath('./ul/li[@class="BatterySeriesProductLi2"]/text()').extract_first()
            meta = response.meta

            meta['subcategory'] = sub_name
            try:
                img = image.get_attribute('src')
            except Exception as e:
                logging.error('Error url' % self.driver.current_url)
                logging.error(e)
                img = ''
            meta['category_image'] = img
            yield scrapy.Request(self.base_url + sub_link, callback=self.parse_subcategory, meta=meta)

    def parse_subcategory(self, response):
        logging.info('Parse Subcategory')
        products_urls = response.xpath('//div[@class="BatteryListProductAll"]/ul/a/@title').extract()
        for product in products_urls:
            url = 'https://www.cameronsino.com/dropship/dropshipproductdetails.html?itemno={}&issearch=true&TabIndex=US'.format(product)
            yield scrapy.Request(url, callback=self.parse_product, meta=response.meta)

        next_page = response.xpath('//a[text()="Next"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(self.base_url + next_page, callback=self.parse_subcategory, meta=response.meta)

    def parse_product(self, response):
        item = CameronsinoScraperItem()
        # pdb.set_trace()
        item['url'] = response.url
        item['Categories'] = response.meta['category'].strip()
        item['SubCategories'] = response.meta['subcategory'].strip()
        item['CategoryImage'] = response.meta['category_image']
        item['SKU'] = response.xpath('//td[@class="detail-mtit"]/text()').extract_first().strip()
        item['Bar_Code'] = self.get_data_by_name(response, "EAN Code:")
        item['Brand'] = ', '.join([i.strip() for i in response.xpath('//div[@id="fitmodel"]//div[@class="productshow_brand"]/text()').extract()]).strip()
        item['Volts'] = self.get_data_by_name(response, "Voltage:")
        item['Type'] = self.get_data_by_name(response, "Type:")
        item['Capacity'] = self.get_data_by_name(response, "Capacity:")
        item['Color'] = self.get_data_by_name(response, "Color:")
        item['Dimension'] = self.get_data_by_name(response, "Dimension:")
        item['Price'] = self.get_data_by_name(response, "Price")
        new_weight = self.get_data_by_name(response, "Net Weight:")
        item['NetWeightGrams'] = new_weight.split('/')[0]
        item['NetWeightPounds'] = new_weight.split('/')[-1]
        gross_weight = self.get_data_by_name(response, "Gross Weight:")
        item['GrossWeightGrams'] = gross_weight.split('/')[0]
        item['GrossWeightPounds'] = gross_weight.split('/')[-1]
        item['Part_No'] = ', '.join([i.strip() for i in response.xpath('//div[@id="partno"]//li/text()').extract()])
        item['Fit_Model'] = ', '.join([i.strip() for i in response.xpath('//div[@id="fitmodel"]//li/text()').extract()])
        item['Stock'] = response.xpath('//td[@class="detail-tit" and contains(text(),"{}")]/following::td/span/text()'.format("Stock:")).extract_first()
        item['Condition'] = self.get_data_by_name(response, "Condition:")
        item['MOQ'] = self.get_data_by_name(response, "MOQ:")
        remark = response.xpath('//td[@class="detail-tit"]/b[contains(text(),"{}")]/following::td/span/text()'.format("Remark:")).extract_first()
        if remark:
            remark = remark.strip()
        else:
            remark = ''
        item['Remark'] = remark
        images = response.xpath('//div[@id="spec-list"]//img[contains(@id, "img")]/@src').extract()
        if images:
            item['base_image'] = images[0]
            item['small_image'] = images[0]
            item['thumbnail_image'] = images[0]
            item['additional_images'] = images[1:]
        yield item

    @staticmethod
    def get_data_by_name(response, name):
        # response.xpath('//span[text()="{}"]/following-sibling::small/text()'.format(name)).extract_first()
        data = response.xpath('//td[@class="detail-tit"]/b[text()="{}"]/following::td/text()'.format(name)).extract_first()
        if not data:
            data = response.xpath('//td[@class="detail-tit" and contains(text(),"{}")]/following::td/text()'.format(name)).extract_first()
        if data:
            data = data.strip()
        else:
            data = ''
        return data

    def spider_closed(self, spider):
        try:
            self.driver.close()
        except Exception:
            pass
