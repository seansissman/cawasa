from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<stock_id>[0-9]+)/$', views.summary, name='summary'),
    url(r'^index/(?P<index_id>[0-9]+)/names/$', views.index_names, name='index_names'),
]