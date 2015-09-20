from django.conf.urls import patterns, url,include
from dAuction2 import views,models
from django.contrib import admin
from dAuction2.views import  index

ident="(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/$"
u_initialize="^initialize/"+ident
u_index="^initialize/(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/$"





urlpatterns = patterns('',
        #url(r'^$', views.index, name='index'),

        #url(r'^initialize/(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/$', views.initialize, name='initialize'),
        url(u_initialize, views.initialize, name='initialize'),


        #from OTREE the call is for this url

        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/$', views.index, name='index'),


        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/set_offer/(?P<valUnits>[0-9]{1,2})/(?P<valPrice>[0-9]{1,6})/(?P<valType>[A-Z]{3,4})$', views.set_offer, name='set_offer'),
        #sets the offer (Buy or Sell), and number of units and price

        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/cancel_so/$', views.cancel_so, name='cancel_so'),
        #cancels the offer - is functional? (seems so :)

        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/all_transactions/$', views.all_transactions, name='all_transactions'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/all_standing_market_offers/$', views.all_standing_market_offers, name='all_standing_market_offers'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/my_standing_offer/$', views.my_standing_offer, name='my_standing_offer'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/refresh/$', views.refresh, name='refresh'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/refresh2/$', views.refresh2, name='refresh2'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/show_theory/$', views.show_theory, name='show_theory'),
        url(r'^(?P<group_id>[0-9]{1,2})/(?P<id_in_group>[0-9]{1,2})/dAuction2/stop/$', views.stop, name='stop'),
        # The elements that are refreshed every x(5?) seconds


        #url(r'^about/$', views.about, name='about'),
        url(r'^admin/', include(admin.site.urls)),
        #url(r'^dAuction2/add_number/$', views.add_number, name='add_number'),
        #url(r'^dAuction2/set_offer/$', views.set_offer, name='set_offer'),
        #url(r'^rket_offers/$', views.all_standing_market_offers, name='all_standing_market_offers'),

        #url(r'^set_offer/index/$', index, name="index"),


)