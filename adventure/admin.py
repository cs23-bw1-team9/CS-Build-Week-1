from django.contrib import admin

# Register your models here.
from .models import Room, Player

class RoomAdmin(admin.ModelAdmin):
    pass

class PlayerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Room, RoomAdmin)
admin.site.register(Player, PlayerAdmin)
