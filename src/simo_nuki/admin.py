from django.contrib import admin
from .models import NukiBridge, NukiDevice


@admin.register(NukiBridge)
class NukiBridgeAdmin(admin.ModelAdmin):
    readonly_fields = 'id', 'ip', 'port', 'last_update', 'info'

    def get_queryset(self, request):
        from .tasks import discover_nuki_bridges
        discover_nuki_bridges()
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NukiDevice)
class NukiDeviceAdmin(admin.ModelAdmin):
    list_display = 'name', 'type', 'last_state'
    readonly_fields = (
        'id', 'bridge', 'type', 'name', 'firmware_version', 'last_state'
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
