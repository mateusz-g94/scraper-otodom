#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 00:51:51 2020

@author: thatone

"""

from link_crawler import LinkCrawlerOtoDom
from scraper import ScraperOtoDom
from db_interfaces import DatabaseInt

if __name__ == "__main__":
    
    # PARAMS:
    DELAY = 5
    MIN_DELAY = 2
    SINCE = 1 # timeliness: 1 day back
    
    # 1. Run link crawler, open database connection and initialize scraper
    db = DatabaseInt()
    crawler = LinkCrawlerOtoDom(SINCE)
    scraper = ScraperOtoDom(DELAY, MIN_DELAY)
    crawler.run()
    n_links = crawler.links.qsize()
    print("START")
    print("Number of links: ", str(n_links), '. Estimated time: ', str(round(n_links * DELAY / 60, 1)), ' minutes.')
    
    for url in crawler.get_link():
                
        # 2. Check condition: if url not in database then scrape
        cond = {'url' : url}
        if not db.find_one(cond):
            
            # 3. Scrape offer
            data = scraper.run(url)
            
            # 4. Insert data 
            if not data: # if error 
                data = {'url' : url, 'ERROR' : 1}
            
            db.insert_one(data)
            
        print("Step ", str(crawler.links.qsize()), ' / ', str(n_links))            
            