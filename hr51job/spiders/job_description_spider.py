import scrapy
import re
import logging

from hr51job.items import Hr51JobItem,Hr51JobDetailItem


class JobDescriptionSpider(scrapy.Spider):
    name = "jd51jobSpider"

    _url = r'http://search.51job.com/list/080200,000000,0000,00,9,99, {} ' \
        r',2,{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99' \
        r'&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&' \
        r'fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='

    def start_requests(self):


        keys = {
            '项目经理',
            'Python',
            '数据分析师',
            'BI',
            '数据挖掘'
        }

        for searchKey in keys:
            search_url = self._url.format(searchKey, 1)

            yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):

        total_pages =  response.css('.dw_page span::text').re(r'共(\w+)页，到第')[0]
        cur_page = response.css('#jump_page::attr(value)').extract_first()
        next_page = int(cur_page) + 1
        key = response.css('#kwdselectid::attr(value)').extract_first().strip()
        next_url = self._url.format(key, next_page)

        jobs = response.css('#resultList .el:not(.el.title)')
        count = 1
        for job in jobs:
            jobitem = Hr51JobItem()

            jobitem['job_id'] = job.css('input[name=delivery_jobid]::attr(value)').extract_first()
            jobitem['job_search_name'] = key
            jobitem['job_name'] = job.css('.t1 span a::text').extract_first().strip()
            jobitem['job_company'] = job.css('.t2 a::text').extract_first()
            jobitem['job_area'] = job.css('.t3::text').extract_first()
            jobitem['job_salary'] = job.css('.t4::text').extract_first()
            if not job.css('.t4::text').extract_first() is None:
                self.analysis_salary(jobitem, job.css('.t4::text').extract_first())
            else:
                jobitem['job_salary_min'] = 0
                jobitem['job_salary_max'] = 0
                jobitem['job_salary_by_year'] = False
            jobitem['job_publish_date'] = job.css('.t5::text').extract_first()

            detail_url = job.css('.t1 span a::attr(href)').extract_first()
            jobitem['job_detail_url'] = detail_url
            yield scrapy.Request(url=detail_url, callback=self.parse_detail)

            count = count + 1
            self.log(count)
            yield jobitem

        if int(cur_page) < int(total_pages):
            # print(r'curpage:{},totalpage:{}'.format(cur_page, total_pages))
            yield scrapy.Request(url=next_url, callback=self.parse)

    def analysis_salary(self, jobitem, salary_text):

        if len(re.findall(r'(.+)-(.+)万/月', salary_text)) > 0:
            # self.log(re.findall(r'(.+)-(.+)万/月', salary_text))
            jobitem['job_salary_min'] = float(re.findall(r'(.+)-(.+)万/月', salary_text)[0][0]) * 10000
            jobitem['job_salary_max'] = float(re.findall(r'(.+)-(.+)万/月', salary_text)[0][1]) * 10000
            jobitem['job_salary_by_year'] = False

        elif len(re.findall(r'(.+)-(.+)千/月', salary_text)) > 0:
            # self.log(re.findall(r'(.+)-(.+)千/月', salary_text))
            jobitem['job_salary_min'] = float(re.findall(r'(.+)-(.+)千/月', salary_text)[0][0]) * 1000
            jobitem['job_salary_max'] = float(re.findall(r'(.+)-(.+)千/月', salary_text)[0][1]) * 1000
            jobitem['job_salary_by_year'] = False

        elif len(re.findall(r'(.+)元/天', salary_text)) > 0:
            jobitem['job_salary_min'] = float(re.findall(r'(.+)元/天', salary_text)[0]) * 20
            jobitem['job_salary_max'] = float(re.findall(r'(.+)元/天', salary_text)[0]) * 20
            jobitem['job_salary_by_year'] = False

        elif len(re.findall(r'(.+)千以下/月', salary_text)) > 0:
            jobitem['job_salary_min'] = float(re.findall(r'(.+)千以下/月', salary_text)[0]) * 1000
            jobitem['job_salary_max'] = float(re.findall(r'(.+)千以下/月', salary_text)[0]) * 1000
            jobitem['job_salary_by_year'] = False

        elif len(re.findall(r'(.+)-(.+)万/年', salary_text)) > 0:
            # self.log(re.findall(r'(.+)-(.+)万/年', salary_text))
            jobitem['job_salary_min'] = int(float(re.findall(r'(.+)-(.+)万/年', salary_text)[0][0]) * 10000 / 12)
            jobitem['job_salary_max'] = int(float(re.findall(r'(.+)-(.+)万/年', salary_text)[0][1]) * 10000 / 12)
            jobitem['job_salary_by_year'] = True

        else:
            self.log("薪资有其他规则的数据存在 %s" % salary_text, logging.ERROR)
            jobitem['job_salary_min'] = 0
            jobitem['job_salary_max'] = 0
            jobitem['job_salary_by_year'] = False

    def parse_detail(self, response):
        job_detai_item = Hr51JobDetailItem()

        job_detai_item['job_id'] = response.css('#hidJobID::attr(value)').extract_first()

        if len(response.css('.msg.ltype::text').extract_first().replace('\t','')
                                              .replace('\r\n','').replace('\xa0','').replace(' ','').split('|'))>1:
            job_detai_item['job_company_type'] = (response.css('.msg.ltype::text').extract_first().replace('\t','')
                                                  .replace('\r\n','').replace('\xa0','').replace(' ','').split('|')[0])
            job_detai_item['job_company_size'] = (response.css('.msg.ltype::text').extract_first().replace('\t','')
                                                  .replace('\r\n','').replace('\xa0','').replace(' ','').split('|')[1])
            job_detai_item['job_company_industry_type_total'] = (response.css('.msg.ltype::text').extract_first()
                                                                 .replace('\t','').replace('\r\n','').replace('\xa0','')
                                                                 .replace(' ','').split('|')[2].split(',')[0])
            if len(response.css('.msg.ltype::text').extract_first()
                    .replace('\t','').replace('\r\n','').replace('\xa0','')
                                         .replace(' ','').split('|')[2].split(',')) > 1:
                # 如果有子类的行业信息的场合

                job_detai_item['job_company_industry_type_total'] = (response.css('.msg.ltype::text').extract_first()
                                                                     .replace('\t', '').replace('\r\n', '')
                                                                     .replace('\xa0', '')
                                                                     .replace(' ', '').split('|')[2].split(',')[0])

                job_detai_item['job_company_industry_type_detail']= (response.css('.msg.ltype::text').extract_first()
                                                                     .replace('\t','').replace('\r\n','').replace('\xa0','')
                                                                     .replace(' ','').split('|')[2].split(',')[1])
            else:
                job_detai_item['job_company_industry_type_total'] = (response.css('.msg.ltype::text').extract_first()
                                                                     .replace('\t', '').replace('\r\n', '')
                                                                     .replace('\xa0', '')
                                                                     .replace(' ', '').split('|')[2])
                job_detai_item['job_company_industry_type_detail'] = ''
        else:
            job_detai_item['job_company_type'] = response.css('.msg.ltype::text').extract_first()
            job_detai_item['job_company_size'] = ''
            job_detai_item['job_company_industry_type_total'] = ''
            job_detai_item['job_company_industry_type_detail'] = ''

        job_detai_item['job_expect_year'] = response.css('.tCompany_main .sp4::text').extract()[0][:1]
        job_detai_item['job_expect_education'] = (response.css('.tCompany_main .sp4::text').extract()[1]
                if response.css('.tCompany_main .sp4::text').extract()[1] in ['大专','本科','硕士','博士'] else '')
        job_detai_item['job_expect_people_count'] = (response.css('.tCompany_main .sp4::text').extract()[2]
            if job_detai_item['job_expect_education'] != '' else response.css('.tCompany_main .sp4::text').extract()[1])

        job_detai_item['job_company_welfare'] = ','.join(response.css('.tCompany_main .t2 span::text').extract())
        job_detai_item['job_description'] = (','.join(response.css('.tBorderTop_box .bmsg.job_msg.inbox::text')
                                                    .extract()).replace('\t','').replace('\r\n','').replace('\xa0',''))
        if len(response.css('.tBorderTop_box .bmsg.inbox .fp').re(r'<p class="fp">\r\n\t\t\t\t\t\t\t\t'
                                                                  r'<span class="label">上班地址：</span>'
                                                                  r'(.+)\t\t\t\t\t\t\t</p>')) > 0:
            job_detai_item['job_place'] = (response.css('.tBorderTop_box .bmsg.inbox .fp').
                                           re(r'<p class="fp">\r\n\t\t\t\t\t\t\t\t<span class="label">上班地址：'
                                              r'</span>(.+)\t\t\t\t\t\t\t</p>')[0])
        else:
            job_detai_item['job_place'] = ''

        job_detai_item['job_company_info'] = (','.join(response.css('.tBorderTop_box .tmsg.inbox::text').extract())
                                              .replace('\r\n','').replace('\t','').replace('\xa0',''))
        yield job_detai_item