from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class AccountRoleFilter(admin.SimpleListFilter):
    """Filter users by admin/registered account role."""

    title = 'role'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            ('registered', 'Registered'),
            ('admin', 'Admin'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'registered':
            return queryset.filter(is_staff=False)
        if value == 'admin':
            return queryset.filter(is_staff=True)
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = ['id', 'name', 'email', 'get_role', 'created_at', 'is_active']
    list_filter = [AccountRoleFilter, 'is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']

    def get_role(self, obj):
        return 'Admin' if obj.is_staff else 'Registered'
    get_role.short_description = 'Role'


admin.site.site_header = 'AI-Powered Exam Checker Admin'
admin.site.site_title = 'Exam Checker Admin'
admin.site.index_title = 'System Monitoring and Management'
