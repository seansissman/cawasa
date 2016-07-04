from django.conf.urls import url

from . import views

app_name = 'stocks'  # Needed for namespacing with templates eg. 'stocks:summary'
urlpatterns = [
    url(r'^$', views.index, name='index'),
#    url(r'^(?P<stock_id>[0-9]+)/$', views.summary, name='summary'),
    url(r'^(?P<pk>[0-9]+)/$', views.SummaryView.as_view(), name='summary'),   # generic view
    url(r'^indexes/$', views.IndexView.as_view(), name='indexes'),  # generic view

    url(r'^index_history/$', views.IndexHistoryView.as_view(), name='index_history'),

    url(r'^index/(?P<index_id>[0-9]+)/names/$', views.index_names, name='index_names'),
]

# url(r'^(?P<stock_id>[0-9]+)/$', views.summary, name='summary'),   # non-generic view
