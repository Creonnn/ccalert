from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re

class Scraper:

    @staticmethod
    async def update(response, status):
        '''
        Scrapes GPU image link, price, and availability.
        '''
        if response:
            soup = BeautifulSoup(response, 'html.parser')
            img = await Scraper.__get_img(soup)
            price = await Scraper.__get_price(soup)
            availability = await Scraper.__get_availability(soup)

            if not (img and price and availability):
                return None, status
            
            img = img["src"]
            price = price.text.strip()
            price = float(re.sub(r'[^\d.]', '', price)) 

            return {'img': img, 'price': price, 'availability': availability}, status
        
        return {'img': '', 'price': 0, 'availability': {}}, status

    @staticmethod
    async def __get_img(html) -> str:
        '''
        Scrapes img link off of html.
        '''
        return html.find("img", attrs={"id": "product-cover-image"}) 
    
    @staticmethod
    async def __get_price(html) -> float:
        '''
        Scrapes price off of html.
        '''
        return html.find(attrs={"class": "current-price-value f-32 f-xs-17 fm-SegoeUI-Bold fm-xs-SF-Pro-Display-Bold font-weight-xs-bold"})
    
    @staticmethod
    async def __get_availability(html) -> dict:
        '''
        Scrapes stock location and quantity from html.
        '''
        availability = {}

        stock_info = await Scraper.__parse_html(html)
        if not stock_info:
            return 
        stock_info = [s.text for s in stock_info]

        for stock in stock_info:
            data = stock.split('\n')
            location = data[1]
            quantity = data[2].replace('+', '')
            availability[location] = int(quantity)

        online = html.find(class_='online-box py-1 px-2 f-16 d-inline-block mb-2')
        online_quantity = int(online.text.split('\n')[3].replace('+', '').strip())
        availability['Online'] = online_quantity

        return availability
    
    @staticmethod
    async def __parse_html(html):
        return await asyncio.to_thread(html.find_all, class_=['row mx-0 align-items-center col d-flex f-18 font-weight-bold mt-1_5 px-0 c-1C4AC4',\
                                                                'row mx-0 align-items-center col d-flex f-18 font-weight-bold mt-1_5 px-0 c-333'])
    

if __name__ == '__main__':
    pass




