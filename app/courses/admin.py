from django.contrib import admin
from courses.models import CoursePackage, Purchase

class CoursePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'hours', 'price', 'description')
    search_fields = ('name', 'description')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('student', 'package', 'purchase_date', 'hours_added', 'amount_paid')
    list_filter = ('purchase_date', 'package')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'package__name')
    date_hierarchy = 'purchase_date'

admin.site.register(CoursePackage, CoursePackageAdmin)
admin.site.register(Purchase, PurchaseAdmin)