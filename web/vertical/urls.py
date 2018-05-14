# -*- coding=utf-8 -*-


from . import views
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    # url(r'^$', views.IndexView.as_view(), name = 'index'),
    # url(r'^download_resume$', views.download_resume, name = 'download_resume'),
    url(r'^seeds/$', views.SeedListView.as_view(), name = 'seeds'),
    url(r'^seed/$', views.SeedView.as_view(), name = 'seed'),
    url(r'^addseed/$', views.AddSeedView.as_view(), name = 'addseed'),
]
