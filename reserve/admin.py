from django.contrib import admin
from .models import Reserve, TimeSlot, Campus

class ReserveAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_name', 'num_person', 'telephone_number', 'campus', 'email', 'date', 'hour', 'description', 'status', 'created_at', 'time_slot')
    list_filter = ('campus', 'status')
    search_fields = ('name', 'last_name', 'telephone_number', 'email')



admin.site.register(Reserve, ReserveAdmin)
admin.site.register(TimeSlot)
admin.site.register(Campus)