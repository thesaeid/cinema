from django.urls import path

from . import apis

urlpatterns = [
    # =============this is what the task wanted===============
    path("rooms/", apis.RoomAPI.as_view(), name="room_list"),
    path("rooms/<int:pk>/", apis.RoomAPI.as_view(), name="room_detail"),
    path(
        "rooms/<int:pk>/screenings/",
        apis.ScreeningRoomAPI.as_view(),
        name="screening_room_list",
    ),
    path(
        "rooms/<int:pk>/screenings/<int:screening_pk>/",
        apis.ScreeningRoomAPI.as_view(),
        name="screening_room_detail",
    ),
    path("bookings/", apis.BookingAPI.as_view(), name="booking_list"),
    path("bookings/<int:pk>/", apis.BookingAPI.as_view(), name="booking_detail"),
    # ========================================================
    # =====================this is extra======================
    path(
        "rooms/<int:pk>/screenings/seats",
        apis.ScreeningRoomSeatAPI.as_view(),
        name="screening_room_seat_list",
    ),
    path("screenings/", apis.ScreeningAPI.as_view(), name="screening-list"),
    path("screenings/<int:pk>/", apis.ScreeningAPI.as_view(), name="screening-detail"),
    path(
        "screenings/<int:pk>/seats/",
        apis.ScreeningSeatsAPI.as_view(),
        name="screening-seats",
    ),
    path("movies/", apis.MovieAPI.as_view(), name="movie_list"),
    path("movies/<int:pk>/", apis.MovieAPI.as_view(), name="movie_detail"),
]
