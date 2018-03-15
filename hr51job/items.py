# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Hr51JobItem(scrapy.Item):
    # define the fields for your item here like:
    job_search_name = scrapy.Field()
    job_id = scrapy.Field()
    job_name = scrapy.Field()
    job_company = scrapy.Field()
    job_area = scrapy.Field()
    job_salary = scrapy.Field()
    job_salary_min = scrapy.Field()
    job_salary_max = scrapy.Field()
    job_salary_by_year = scrapy.Field()
    job_publish_date = scrapy.Field()
    job_detail_url = scrapy.Field()


class Hr51JobDetailItem(scrapy.Item):

    job_id = scrapy.Field()
    job_company_type = scrapy.Field()
    job_company_size = scrapy.Field()
    job_company_industry_type_total = scrapy.Field()
    job_company_industry_type_detail = scrapy.Field()

    job_expect_year = scrapy.Field()
    job_expect_education = scrapy.Field()
    job_expect_people_count = scrapy.Field()
    job_company_welfare = scrapy.Field()
    job_description = scrapy.Field()
    job_place = scrapy.Field()
    job_company_info = scrapy.Field()