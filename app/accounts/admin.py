# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, Student, Instructor

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('user_type', 'phone_number', 'address')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'remaining_hours', 'get_email')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Nom complet'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

class InstructorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'specialization', 'get_email')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'specialization')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Nom complet'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Instructor, InstructorAdmin)