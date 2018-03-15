# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.conf import settings
from hr51job.items import Hr51JobItem,Hr51JobDetailItem
from datetime import datetime

class Hr51JobPipeline(object):
    def process_item(self, item, spider):
        host = settings['MYSQL_HOSTS']
        user = settings['MYSQL_USER']
        psd = settings['MYSQL_PASSWORD']
        db = settings['MYSQL_DB']
        c = settings['CHARSET']
        port = settings['MYSQL_PORT']

        con = pymysql.connect(host=host, user=user, passwd=psd, db=db, charset=c, port=port)
        cue = con.cursor()

        if isinstance(item, Hr51JobItem):

            try:
                cue.execute("insert into t_job (ctime,job_search_name,job_id,job_name,job_company,job_area,job_salary,"
                            "job_salary_min,job_salary_max,job_salary_by_year,job_publish_date,job_detail_url)"
                            " values(now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                            ,[ item['job_search_name'],item['job_id'],item['job_name'],item['job_company']
                            ,item['job_area'],item['job_salary']
                            ,item['job_salary_min'] if item['job_salary_min'] else 0
                            ,item['job_salary_max'] if item['job_salary_max'] else 0
                            ,item['job_salary_by_year'] if item['job_salary_by_year'] else 0
                            ,item['job_publish_date'],item['job_detail_url']])
                print("insert success")
            except Exception as e:
                print('Insert error:',e)
                con.rollback()
            else:
                con.commit()
            con.close()
        elif isinstance(item, Hr51JobDetailItem):
            try:
                cue.execute("select 1 from t_job where job_id = %s AND date(ctime)=%s",[item['job_id'],
                                                                            datetime.now().strftime('%Y-%m-%d')])
                if cue.rowcount > 0:
                    cue.execute("update t_job set job_company_type = %s,job_company_size = %s, "
                                "job_company_industry_type_total = %s ,job_company_industry_type_detail = %s,"
                                "job_expect_year = %s, job_expect_education = %s, job_expect_people_count = %s,"
                                "job_company_welfare = %s,job_description = %s,job_place = %s, job_company_info = %s "
                                "WHERE job_id = %s AND date(ctime)=%s"
                                ,[ item['job_company_type'],item['job_company_size']
                                ,item['job_company_industry_type_total'],item['job_company_industry_type_detail']
                                ,item['job_expect_year'] if item['job_expect_year'] else 0
                                ,item['job_expect_education'],item['job_expect_people_count']
                                ,item['job_company_welfare'],item['job_description'],item['job_place']
                                ,item['job_company_info'],item['job_id'],datetime.now().strftime('%Y-%m-%d')])
                    print("update success")
            except Exception as e:
                print('update error:',e)
                con.rollback()
            else:
                con.commit()
            con.close()
        return item

