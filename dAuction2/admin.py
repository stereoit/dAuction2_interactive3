# Register your models here.
from django.contrib import admin
from dAuction2.models import Group, Player

class PlayerAdmin(admin.ModelAdmin):
    fields = ['group','name', 'money']
    list_display = ('group', 'name', 'money')

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {'name':('name',)}


admin.site.register(Player,PlayerAdmin)
admin.site.register(Group, GroupAdmin)