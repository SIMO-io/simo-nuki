from django.conf.urls import include, url
from django.urls import path
from .views import callback

urlpatterns = [
    url(r"^callback/$", callback, name='nuki-callback'),
]
