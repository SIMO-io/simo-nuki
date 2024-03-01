from django.urls import include, re_path
from .views import callback

urlpatterns = [
    re_path(r"^callback/$", callback, name='nuki-callback'),
]
