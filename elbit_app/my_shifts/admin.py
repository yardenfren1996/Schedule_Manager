from django.contrib import admin
from .models import WorkerProfileInfo, Shift


class ShiftAdmin(admin.ModelAdmin):
    search_fields = ['date', 'shift_time']

    list_filter = ['date', 'shift_time']

    list_display = ['date', 'shift_time', 'user']


class WorkerAdmin(admin.ModelAdmin):
    search_fields = ['worker_number', 'name']


# Register your models here.
admin.site.register(WorkerProfileInfo, WorkerAdmin)
admin.site.register(Shift, ShiftAdmin)
