from django.contrib import admin
from .models import SuperAdmin, Admin, Manager, Court, Booking, Membership_Plan, Membership, Customer, slot, MembershipBooking, Inventory
# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

class SuperAdminAdmin(UserAdmin):
    model = SuperAdmin
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

# admin.site.register(SuperAdmin, SuperAdminAdmin)
admin.site.register(Admin)
admin.site.register(Manager)
admin.site.register(Court)
admin.site.register(Booking)
admin.site.register(Membership_Plan)
admin.site.register(Membership)
admin.site.register(slot)
admin.site.register(MembershipBooking)
admin.site.register(Inventory)


admin.site.site_header = 'Ace Bounce'
admin.site.site_title = 'Ace Bounce'
