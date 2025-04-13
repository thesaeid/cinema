from datetime import timezone
import re
from tracemalloc import start
from unittest.mock import Base
from rest_framework import serializers
from .models import Room, Movie, Screening, Seat, Screening, Booking


class RoomSerializer(serializers.ModelSerializer):
    screenings = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "rows", "seats_in_row", "screenings"]

    def get_screenings(self, obj):
        screenings = Screening.objects.filter(room=obj)
        return BaseScreeningSerializer(screenings, many=True).data


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class BaseMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "duration", "poster"]
        read_only_fields = ["id"]


class BaseScreeningSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(source="movie.title", read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Screening
        fields = [
            "movie",
            "start_time",
        ]


class ScreeningSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField(source="movie.title", read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    room = serializers.StringRelatedField(source="room.name", read_only=True)

    class Meta:
        model = Screening
        fields = [
            "id",
            "movie",
            "room",
            "start_time",
            "end_time",
        ]


class BaseSeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = ["id", "row", "seat_number"]
        read_only_fields = ["id"]


class SeatSerializer(BaseSeatSerializer):
    is_available = serializers.SerializerMethodField()
    screening = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = [
            "id",
            "row",
            "seat_number",
            "screening",
            "room",
            "is_available",
        ]
        read_only_fields = ["screening", "room"]

    def get_screening(self, obj):
        return obj.screening.movie.title

    def get_room(self, obj):
        return obj.room.name

    def get_is_available(self, obj):
        # Check if the seat is booked for the screening
        booked_seat_ids = Booking.objects.filter(screening=obj.screening).values_list(
            "seat_id", flat=True
        )

        return obj.id not in booked_seat_ids


class BaseBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    screening = serializers.PrimaryKeyRelatedField(
        queryset=Screening.objects.all(), write_only=True
    )
    seat = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(), write_only=True
    )
    user = serializers.StringRelatedField(source="user.username", read_only=True)


class BookingSerializer(serializers.ModelSerializer):
    purchase_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    screening = serializers.PrimaryKeyRelatedField(
        queryset=Screening.objects.all(), write_only=True
    )
    seat = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(), write_only=True
    )
    user = serializers.StringRelatedField(source="user.username", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "screening", "seat", "user", "purchase_time"]
        read_only_fields = ["user", "purchase_time"]

    def create(self, validated_data):
        # Set the current user as the booking user
        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["user"] = user
        return super().create(validated_data)


class ScreeningDetailSerializer(serializers.ModelSerializer):
    movie = BaseMovieSerializer()
    room = serializers.StringRelatedField(source="room.name", read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    available_seats = serializers.SerializerMethodField()
    booked_seats = serializers.SerializerMethodField()

    class Meta:
        model = Screening
        fields = [
            "id",
            "movie",
            "room",
            "start_time",
            "available_seats",
            "booked_seats",
        ]

    def get_booked_seats(self, obj):
        bookings = Booking.objects.filter(screening=obj)
        return BaseSeatSerializer(
            [booking.seat for booking in bookings], many=True, context=self.context
        ).data

    def get_available_seats(self, obj):
        # Get all seats in the screening's room
        all_seats = Seat.objects.filter(room=obj.room, screening=obj)

        # Get booked seats for this screening
        booked_seat_ids = Booking.objects.filter(screening=obj).values_list(
            "seat_id", flat=True
        )

        # Filter available seats
        available_seats = all_seats.exclude(id__in=booked_seat_ids)

        return BaseSeatSerializer(available_seats, many=True, context=self.context).data
