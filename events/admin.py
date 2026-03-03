from django.contrib import admin
from .models import Event, TicketType


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [TicketTypeInline]
    list_display = ("title", "date", "location", "category")
    list_filter = ("category",)
    search_fields = ("title", "location")


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "available_seats", "priority")
