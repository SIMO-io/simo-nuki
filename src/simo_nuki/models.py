from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from dirtyfields import DirtyFieldsMixin
from simo.core.models import Component, Gateway


class NukiBridge(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=20, null=True, blank=True)
    info = models.JSONField(default={})

    def __str__(self):
        return f"{self.id} on http://{self.ip}:{self.port}"


class NukiDevice(DirtyFieldsMixin, models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    bridge = models.ForeignKey(
        NukiBridge, null=True, on_delete=models.SET_NULL
    )

    ip = models.GenericIPAddressField(null=True)
    port = models.PositiveIntegerField(null=True)
    token = models.CharField(max_length=20, null=True, blank=True)

    type = models.PositiveIntegerField(choices=(
        (0, "smartlock - Nuki Smart Lock 1.0/2.0"),
        (2, "opener - Nuki Opener"),
        (3, "smartdoor - Nuki Smart Door"),
        (4, "smartlock3 - Nuki Smart Lock 3.0 (Pro)")
    ), default=4)
    name = models.CharField(max_length=100, default='')
    firmware_version = models.CharField(max_length=100, default='')

    last_state = models.CharField(max_length=50, default='')
    last_state_data = models.JSONField(default={})
    last_update = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.name} ({self.id})'

    def lock(self, run_async=True):
        from .tasks import device_action
        if run_async:
            device_action.delay(self.id, 'lock')
        else:
            device_action(self.id, 'lock')

    def unlock(self, run_async=True):
        from .tasks import device_action
        if run_async:
            device_action.delay(self.id, 'unlock')
        else:
            device_action(self.id, 'unlock')

    def components(self):
        return Component.objects.filter(
            gateway__type='NukiDevices', config__nuki_device=self.id
        )


Gateway.objects.get_or_create(type='NukiDevices')


@receiver(post_save, sender=NukiDevice)
def receive_change_to_component(sender, instance, *args, **kwargs):
    receive_val = None
    if 'last_state' in instance.get_dirty_fields():
        if instance.last_state == 'unlocked':
            receive_val = False
        elif instance.last_state == 'locked':
            receive_val = True

    for component in instance.components:
        if 'batteryChargeState' in instance.last_state_data \
        and component.battery_level != instance.last_state_data['batteryChargeState']:
            component.battery_level = instance.last_state_data['batteryChargeState']
            component.save(update_fields=['battery_level'])
        if receive_val != None:
            component.controller._receive_from_device(receive_val)


@receiver(post_save, sender=Component)
def set_initial_state(sender, instance, created, *args, **kwargs):
    if not created:
        return
    if instance.gateway.type == 'NukiDevices':
        device = NukiDevice.objects.get(id=instance.config['nuki_device'])
        if device.last_state_data['batteryChargeState']:
            instance.battery_level = device.last_state_data['batteryChargeState']
        if device.last_state == 'locked':
            instance.value = True
        elif device.last_state == 'unlocked':
            instance.value = False
        instance.save()

