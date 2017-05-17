from django.contrib import admin

# Register your models here.

from will_common.models import UserProfile, OrgGroup
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class EmployeeInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
