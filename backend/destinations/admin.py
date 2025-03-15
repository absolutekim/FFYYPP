from django.contrib import admin
from .models import Location, Like, Review

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'country')
    search_fields = ('name', 'description', 'category', 'city', 'country')
    list_filter = ('category', 'country')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'location__name')
    date_hierarchy = 'created_at'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'rating', 'sentiment', 'created_at')
    list_filter = ('rating', 'sentiment', 'created_at')
    search_fields = ('user__username', 'location__name', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('sentiment', 'sentiment_score', 'keywords')