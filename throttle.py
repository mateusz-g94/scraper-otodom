#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 02:09:53 2020

@author: thatone
"""

import urllib.parse as up
import datetime
import time
import numpy as np

# Class Throttling downloads 
class Throttle:
    """ Add a delay between downloads to the same domain in seconds
    """
    def __init__(self, mean_delay, st = 3, min_seconds = 1):
        # the amout of delay between downloads or each domain 
        self.mean_delay = mean_delay
        self.st = st
        self.min_seconds = min_seconds
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def draw_seconds(self):
        draw = int(np.random.normal(self.mean_delay, self.st))
        return draw if draw >= 0 else 1
    
    def wait(self, url):
        domain = up.urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        
        if self.mean_delay > 0 and last_accessed is not None:
            sleep_secs = self.mean_delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                if self.min_seconds > 0:
                    time_sleep = max(self.min_seconds, self.draw_seconds())
                else:
                    time_sleep = self.draw_seconds()
                # domain has been accessed recently 
                # need to sleep
                time.sleep(time_sleep)
        # update the last accessed time 
        self.domains[domain] = datetime.datetime.now()
        