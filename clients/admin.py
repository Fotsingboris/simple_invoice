from django.contrib import admin

from .models import Client, Domain
from django_tenants.admin import TenantAdminMixin


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'organisation_code', 'on_trial', 'created_on', 'is_active', 'paid_until', 'country', 'city', 'address_line1', 'address_line2', 'created', 'modified')
    list_filter = ('on_trial', 'is_active')
    
    
@admin.register(Domain)
class DomainAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary') 