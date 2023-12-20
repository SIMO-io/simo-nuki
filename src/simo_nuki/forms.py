from django import forms
from django.db.models import Q
from simo.core.forms import BaseComponentForm
from .models import NukiDevice


class BasicNukiComponentConfigForm(BaseComponentForm):
    nuki_device = forms.ModelChoiceField(queryset=NukiDevice.objects.all())



class NukiLock(BasicNukiComponentConfigForm):
    pass