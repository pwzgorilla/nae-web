from django.conf.urls import patterns,url

from overview import views

urlpatterns = patterns('',
    url(r'^$',views.index,name='index')
)
