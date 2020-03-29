#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 18:10:17 2020

@author: thatone
"""

import requests
from bs4 import BeautifulSoup
from throttle import Throttle
import re
import json
import datetime


class ScraperOtoDom:
    """
    Offer scraper uses throttling,  but doesnt change proxy and user agent.
    """
    def __init__(self, th_sec, min_seconds = 2):
        self.thr = Throttle(th_sec, min_seconds = min_seconds)
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.137 Safari/537.36 OPR/67.0.3575.79'
        
    def __download_html(self, url):
        self.thr.wait(url) # Wait 
        response = requests.get(url, headers={'User-Agent' : self.user_agent})
        content = response.content
        self.soup =  BeautifulSoup(content, "html.parser")
    
    def __text_to_num(self, text):
        num = ''.join(x for x in re.findall(r'[0-9]', text))
        if num:
            return int(num)
        else:
            return None
        
    def __get_title(self):
        return self.soup.find("h1", class_="css-1ld8fwi").text

    def __get_price(self):
        price = self.soup.find("div", class_="css-1vr19r7").text
        return self.__text_to_num(price)
    
    def __get_offer_details(self):
        det_to_con = ['Powierzchnia', 'Czynsz - dodatkowo', 'Piętro', 'Liczba pokoi', 'Liczba pięter', 'Rok budowy', 'Kaucja']
        det_dict = {}
        det_list = self.soup.find("div", class_="css-1ci0qpi").find_all("li")
        for det in det_list:
            text = det.text.split(":")
            if text[0] in det_to_con:
                det_dict[text[0]] = self.__text_to_num(text[1])
            else:
                det_dict[text[0]] = text[1]
        return det_dict
    
    def __get_description(self):
        text = self.soup.find("div", class_="css-1bi3ib9").text
        text = text.replace(u'\xa0', u'') # Encoding errors
        return text
    
    def __get_add_list(self):
        try:
            add_list = []
            for add_el in self.soup.find("div", class_ = "css-1bpegon").find_all("li"):
                add_list.append(add_el.text)
            return add_list
        except: 
            return []
    
    def __get_address(self):
        addr_dict = {}
        for part in self.soup.find_all("script", type='application/ld+json'):
            data = json.loads(part.text)
            # Two try'ies, each element can be found in other parts
            try:
                addr_dict['address'] = data['@graph'][0]['address']['streetAddress']
            except KeyError:
                pass
            try:
                addr_dict['latitude'] = data['@graph'][0]['geo']['latitude']
                addr_dict['longitude'] = data['@graph'][0]['geo']['longitude']
            except KeyError:
                pass
        return addr_dict
    
    def __get_offer_id(self):
        list_ids = []
        names = ['id_offer', 'id_agency']
        for part in self.soup.find("div", class_ = "css-kos6vh").text.split(':')[1:]:
            list_ids.append(self.__text_to_num(part))
        return dict(zip(names, list_ids))
            
    def __get_offer_cr_date(self):
        cr_date = ''
        for part in self.soup.find_all("script", type='application/json'):
            data = json.loads(part.text)
            try:
                cr_date = data['initialProps']['meta']['created_at'][0:10]
            except:
                pass
        return cr_date
    
    def run(self, url):
        """
        Parameters
        ----------
        url : str
            offer url

        Returns
        -------
        data : dict 
            dictionary like json object; all information collected 

        """
        try:
            self.__download_html(url)
            data = {
                'title' : self.__get_title(),
                'price' : self.__get_price(),
                'details' : self.__get_offer_details(),
                'description' : self.__get_description(),
                'extra' : self.__get_add_list(),
                'geo' : self.__get_address(),
                'ids' : self.__get_offer_id(),
                'created_date' : self.__get_offer_cr_date(),
                'url' : url,
                'download_date' : datetime.date.today().strftime('%Y-%m-%d')
                }
            return data
        except:
            return None
    
if __name__ == '__main__':
    test_url = 'https://www.otodom.pl/oferta/2pok-w-apartamentowcu-blisko-metra-ID45gnf.html#c88f980bdf'
    sc = ScraperOtoDom(3).run(test_url)
  
    
    