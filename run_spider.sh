#!/bin/bash

find /home/ubf19/cameronsino_data/ -maxdepth 1 -mtime +30 -type f -delete
cd /home/ubf19/cameronsino_scraper/cameronsino_scraper
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl cameronsino_spider