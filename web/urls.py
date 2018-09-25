from django.conf.urls import url
from web.views import home
from web.views import login_register
from web.views import  my_home


urlpatterns = [
    url(r'^$', home.to_home),
    url(r"^login_register.html$", login_register.show_page, name='show_login_page'),
    url(r"^register$", login_register.register, name="register"),
    url(r"^check_code$", login_register.check_code, name="check_code"),
    url(r"^login$", login_register.login, name="login"),
    url(r"^logout$", login_register.logout, name="logout"),
    url(r'^home.html-(?P<category>\d+)$', home.home, name='home'),
    url(r'^my_home/(?P<surfix>\w+).html$', my_home.my_home, name="my_home"),
    url(r"^my_home/(?P<surfix>\w+)/(?P<category>(category)|(tag)|(time))/(?P<num>\d+-*\d*).html$",  # 0  2017-1
        my_home.article_filter, name="article_filter"),
    url(r"^article_detail/(?P<surfix>\w+)/(?P<article_id>\d+).html$", my_home.article_detail, name="article_detail"),
    url(r"^save_comment$", my_home.save_comment, name="save_comment"),
    url(r'^comment_page_nation$', my_home.comment_page_nation, name="comment_page_nation"),
    url(r'^thumb$', my_home.thumb, name="thumb"),
    url(r'^re_comment$', my_home.re_comment, name="re_comment"),
]



