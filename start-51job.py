#!/usr/bin/python3

from scrapy.cmdline import execute

if __name__ == '__main__':
    execute(['scrapy', 'crawl', 'jd51jobSpider', '--output', 'cards.json'])