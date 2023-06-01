from datetime import datetime
from hashlib import md5

import scrapy
from olxscraper.items import VehicleItem
from scrapy.utils.project import get_project_settings


class OlxSpider(scrapy.Spider):
    name = 'olx'
    allowed_domains = ['olx.com.br']
    start_urls = ['https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios']

    def parse(self, response, **kwargs):
        vehicles = response.css('ul#ad-list>li')
        for vehicle in vehicles:
            vehicle_url = vehicle.xpath('.//a[@data-ds-component="DS-NewAdCard-Link"]/@href').get()
            if vehicle_url is not None:
                yield response.follow(vehicle_url, callback=self.parse_vehicle)

        next_page = response.xpath('.//a[@data-lurker-detail="next_page"]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_vehicle(self, response):
        vehicle_item = VehicleItem()

        # Remove nós do HTML para poupar espaço
        root = response.xpath('/*')
        xpath_patterns = ['.//style', './/path']
        for xp in xpath_patterns:
            node = root.xpath(xp)
            node.drop()

        # Dados do veículo para gerar o hash da página (verificar se houve alteração)
        vehicle_data = response.css('script#initial-data').get()

        # Adiciona os campos do item
        vehicle_item['visited_on'] = datetime.now()
        vehicle_item['category'] = 'LEAF'
        vehicle_item['url'] = response.url
        vehicle_item['html'] = root.get()
        vehicle_item['url_hash'] = md5(response.url.encode()).hexdigest()
        vehicle_item['html_hash'] = md5(vehicle_data.encode()).hexdigest()

        yield vehicle_item
