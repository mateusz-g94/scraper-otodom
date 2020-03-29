#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 00:39:01 2020
    
@author: thatone
"""

import requests
from queue import Queue
from bs4 import BeautifulSoup
from throttle import Throttle

class LinkCrawlerOtoDom:
    """
    Class downloads links from url_start. 
    Parameter since - timeliness of the offer in days. -1 means all history.
    """
    def __init__(self, since = 1, th_sec = 5):
        if since not in [-1,1,3,7,14]: 
            raise Exception('SinceLevelError: since is out of range [-1,1,3,7,14].')
        self.since = since
        self.thr = Throttle(th_sec)
        self.url_start = 'https://www.otodom.pl/wynajem/mieszkanie/warszawa/?' if self.since == -1 else "https://www.otodom.pl/wynajem/mieszkanie/warszawa/?search%5Bdescription%5D=1&search%5Bcreated_since%5D=" + str(self.since) + "&search%5Bregion_id%5D=7&search%5Bsubregion_id%5D=197&search%5Bcity_id%5D=26" 
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.137 Safari/537.36 OPR/67.0.3575.79'
        self.__get_max_page()
        self.links = Queue() 
        
    def __download_html(self, url):
        self.thr.wait(url) # Wait 
        response = requests.get(url, headers={'User-Agent' : self.user_agent})
        content = response.content
        return BeautifulSoup(content, "html.parser")
        
    def __get_max_page(self):
        soup = self.__download_html(self.url_start)
        try:
            self.max_page = int(soup.find("ul", class_="pager").find_all("li")[-2].text)
        except:
            raise Exception('ConvertError: cant find max page.')
        
    def __get_links_from_page(self, url):
        links = set()
        for article in self.__download_html(url).find("div", id="listContainer").find_all("article", {'data-featured-name' : "listing_no_promo"}):
            links.add(article.find("a", href = True)['href'])
        return links
    
    def __range_pages(self):
        for page in range(1, self.max_page + 1):
            yield self.url_start + "&page=" + str(page)
            
    def __get_links_from_pages(self):
        for url in self.__range_pages():
            links = self.__get_links_from_page(url)
            for link in links:
                self.links.put(link)
    
    def run(self):
        """
        Get links starting from self.url_start.
        Method crates Queue with urls.
        """
        print('Estimated crawling time: ', str(self.thr.mean_delay * self.max_page), 'seconds.')
        print('start...')
        self.__get_links_from_pages()
        print('...end')
        
    def get_link(self):
        while True:
            try:
                yield self.links.get_nowait()
            except:
                break
            
if __name__ == "__main__":
    test = LinkCrawlerOtoDom(since = 1)
    test.run()
    print(test.max_page)