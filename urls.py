from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dj_intro_cs.views.home', name='home'),
    # url(r'^dj_intro_cs/', include('dj_intro_cs.foo.urls')),
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    ('^', include('commentbin.urls')),
)
