from django.contrib import admin
from .models import Planner, PlannerItem

class PlannerItemInline(admin.TabularInline):
    model = PlannerItem
    extra = 0

@admin.register(Planner)
class PlannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [PlannerItemInline]

@admin.register(PlannerItem)
class PlannerItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'planner', 'location', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('planner__title', 'location__name', 'notes')
