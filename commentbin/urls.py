from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('commentbin.views',
    url(r'^$','index'),
    url(r'^about/','about'),
    url(r'^help/','sitehelp'),
    url(r'^logout/','logout'),
    url(r'^login/','login'),
    url(r'^(?P<snippet_id>\d+)/$','snippet'),
    url(r'^(?P<snippet_id>\d+)/comments/$','comments'),
    url(r'^(?P<snippet_id>\d+)/comments/(?P<comment_id>\d+)/$','comment'),
    )