from django.db import models


# Create your models here.


class Seed(models.Model):
    name = models.CharField(max_length = 100, default = None, null = True, unique = True)
    description = models.CharField(max_length = 200, default = None, null = True)

    run_interval = models.IntegerField(default = 0, null = True)
    rule_data = models.TextField(default = None, null = True)

    extra = models.CharField(max_length = 200, default = None, null = True)
    status = models.IntegerField(default = 0, null = True)
    last_run_time = models.DateTimeField(null = True)
    create_time = models.DateTimeField(auto_now_add = True)
    uid = models.CharField(max_length = 200, default = None, null = True)

    class Meta:
        db_table = 'vertical_crawler_seed'

        verbose_name = 'seed'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Result(models.Model):
    seed_id = models.IntegerField(default = 0, null = True)
    crawler_name = models.CharField(max_length = 100, default = None, null = True)
    crawler_url = models.CharField(max_length = 1024, default = None, null = True)
    crawler_url_id = models.BigIntegerField(default = 0, null = True)
    origin_data = models.TextField(default = None, null = True, verbose_name = '原始数据')
    extract_data = models.TextField(default = None, null = True, verbose_name = '提取数据')

    create_time = models.DateTimeField(auto_now_add = True, verbose_name = '抓取入库时间')

    class Meta:
        db_table = 'vertical_crawler_result'

        verbose_name = 'result'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.crawler_name
