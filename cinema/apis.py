from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status

from .models import Booking, Room, Movie, Screening, Seat
from .serializers import (
    RoomSerializer,
    MovieSerializer,
    ScreeningSerializer,
    SeatSerializer,
    BookingSerializer,
    ScreeningDetailSerializer,
    BaseSeatSerializer,
    BaseBookingSerializer,
)


class RoomAPI(views.APIView):
    def get(self, request, pk=None):
        if pk:
            room = get_object_or_404(Room, pk=pk)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        else:
            rooms = Room.objects.all()
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data)


class ScreeningRoomSeatAPI(views.APIView):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        screenings = Screening.objects.filter(room=room)
        seats = Seat.objects.filter(room=room)

        screening_serializer = ScreeningSerializer(screenings, many=True)
        seat_serializer = BaseSeatSerializer(seats, many=True)

        return Response(
            {
                "screenings": screening_serializer.data,
                "seats": seat_serializer.data,
            }
        )


class MovieAPI(views.APIView):
    def get(self, request, pk=None):
        if pk:
            movie = get_object_or_404(Movie, pk=pk)
            serializer = MovieSerializer(movie)
            return Response(serializer.data)
        else:
            movies = Movie.objects.all()
            serializer = MovieSerializer(movies, many=True)
            return Response(serializer.data)


class ScreeningRoomAPI(views.APIView):
    def get(self, request, pk, screening_pk=None):
        if screening_pk:
            screening = get_object_or_404(Screening, pk=screening_pk)
            serializer = ScreeningDetailSerializer(screening)
            return Response(serializer.data)
        else:
            room = get_object_or_404(Room, pk=pk)
            screenings = Screening.objects.filter(room=room)
            serializer = ScreeningSerializer(screenings, many=True)
            return Response(serializer.data)


class ScreeningAPI(views.APIView):
    def get(self, request, pk=None):
        if pk:
            screening = get_object_or_404(Screening, pk=pk)
            serializer = ScreeningDetailSerializer(screening)
            return Response(serializer.data)
        else:
            screenings = Screening.objects.all()
            serializer = ScreeningSerializer(screenings, many=True)
            return Response(serializer.data)


class ScreeningSeatsAPI(views.APIView):
    def get(self, request, pk):
        screening = get_object_or_404(Screening, pk=pk)
        seats = Seat.objects.filter(
            screening=screening,
        )
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)


class BookingAPI(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            booking = get_object_or_404(Booking, pk=pk)
            serializer = BookingSerializer(booking)
            return Response(serializer.data)
        else:
            bookings = Booking.objects.filter(user=request.user)
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = request.user
        seat = get_object_or_404(Seat, pk=request.data.get("seat"))
        screening = get_object_or_404(Screening, pk=request.data.get("screening"))
        if seat.screening != screening:
            return Response(
                {
                    "detail": "The selected seat does not belong to the specified screening."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Booking.objects.filter(seat=seat, screening=screening).exists():
            return Response(
                {"detail": "This seat is already booked."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BaseBookingSerializer(data=request.data)
        if serializer.is_valid():
            Booking.objects.create(
                user=user,
                screening=screening,
                seat=seat,
            )
            serializer.instance = Booking.objects.get(
                user=user,
                screening=screening,
                seat=seat,
            )
            serializer = BookingSerializer(serializer.instance)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
