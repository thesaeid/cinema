from django.contrib import admin

from .models import Room, Movie, Screening, Seat, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rows", "seats_in_row")
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 10


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "duration")
    search_fields = ("title",)
    ordering = ("title",)
    list_per_page = 10


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "room", "start_time")
    search_fields = ("movie__title", "room__name")
    ordering = ("start_time",)
    list_per_page = 10


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "row", "seat_number", "screening")
    search_fields = ("screening__movie__title",)
    ordering = ("screening__start_time",)
    list_per_page = 10


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "screening", "seat")
    search_fields = ("user__username", "screening__movie__title")
    list_per_page = 10
