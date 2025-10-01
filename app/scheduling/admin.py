from django.contrib import admin
from scheduling.models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'student', 'instructor', 'location', 'duration')
    list_filter = ('date', 'instructor', 'duration')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'instructor__user__first_name', 
                    'instructor__user__last_name', 'location')
    date_hierarchy = 'date'

admin.site.register(Appointment, AppointmentAdmin)