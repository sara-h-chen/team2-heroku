from django.conf.urls import url
from django.contrib.auth import views as auth_views

import views

urlpatterns = [
    url(r'^newuser/$', views.createUser, name='create_user'),
    url(r'^login/$', views.obtain_auth_token, name='login'),
    url(r'^user/history/$', views.historyHandler),
    url(r'^user/profile/$', views.profileHandler),
    url(r'^user/preferences/$', views.preferenceHandler),
    url(r'^user/search/(?P<username>[a-zA-Z0-9]+)/$', views.findUser),
    url(r'^food/(?P<latitude>-?\d+(?:\.\d+))/(?P<longitude>-?\d+(?:\.\d+))/$', views.foodListHandler),
    url(r'^food/update/(?P<id>[0-9]+)/$', views.updateHandler),
    # url(r'^search/(?P<type>[0-4]{1})/$', views.search, name='search'),
    # url(r'^courgette/(?P<userID>[0-4]{5})/$', views.notifcation, name='notifcations')
    url(r'^function/(?P<user_id>[0-9]+)/$', views.identify),
    url(r'^function/messagesBetween/$', views.getMessagesBetween),
    url(r'^user/(?P<username>[a-zA-Z0-9]+)/messages/$', views.getMessages),
    url(r'^user/(?P<username>[a-zA-Z0-9]+)/contacts/$', views.getContacts),
    url(r'^user/messages/add/$', views.addMessage),
]
