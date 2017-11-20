from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/update_price/$', views.update_price, name='update_price'),
]