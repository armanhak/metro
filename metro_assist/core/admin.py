from django.contrib import admin

# Register your models here.
from .models import (Employee, Request, 
                     Passenger, Smena, 
                     PassengerCategory,
                     Uchastok, WorkTime,
                     Rank,EmployeeSchedule,
                     RequestMethod, RequestStatus,
                     MetroTravelTime, MetroTransferTime,
                     MetroStation



)
@admin.register(Employee)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('initials','work_time', 'work_phone', 'personal_phone')

    search_fields = ('initials', 'work_phone', 'personal_phone' )

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'patronymic', 'tab_number', 'work_time', 'work_phone', 'personal_phone', 'rank')
        }),

    )
@admin.register(Passenger)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name','contact_phone', 'category')

    search_fields = ('name','contact_phone' )

    fieldsets = (
        (None, {
            'fields': ('name','contact_phone',  'category', 'additional_info')
        }),

    )

@admin.register(Request)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('status','id_pas', 'cat_pas', 'datetime','time_over', 'insp_sex_m', 'insp_sex_f', 'id_st1', 'id_st2')

    search_fields = ( 'id_pas', 'status')

    list_filter  =('status',)

@admin.register(PassengerCategory)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Smena)
class UserProfileAdmin(admin.ModelAdmin):
    pass
@admin.register(Uchastok)
class UserProfileAdmin(admin.ModelAdmin):
    pass
@admin.register(WorkTime)
class UserProfileAdmin(admin.ModelAdmin):
    pass
@admin.register(Rank)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(EmployeeSchedule)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('employee','start_work_date', 'smena')
    search_fields = ('employee', )
    list_filter  = ('smena',)

@admin.register(RequestMethod)
class UserProfileAdmin(admin.ModelAdmin):
    pass
@admin.register(RequestStatus)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(MetroTravelTime)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id_st1','id_st2', 'time')
    search_fields = ('id_st1__name_station','id_st2__name_station' )

@admin.register(MetroTransferTime)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id1','id2', 'time')
    search_fields = ('id1__name_station','id2__name_station' )

@admin.register(MetroStation)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name_station','name_line', 'id_line')
    search_fields = ('name_station', )
    list_filter  = ('name_line',)