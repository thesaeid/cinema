from django.conf import settings
from django.db import models
from django.core import validators


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_room_name",
            )
        ]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.DurationField()
    poster = models.ImageField(upload_to="posters/", null=True, blank=True)

    def __str__(self):
        return self.title


class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["room", "start_time"],
                name="unique_room_start_time",
            )
        ]
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.movie.title} at {self.start_time.strftime('%H:%M %p, %d %b %Y')} in {self.room.name}"

    @property
    def end_time(self):
        return self.start_time + self.movie.duration


class Seat(models.Model):
    row = models.IntegerField()
    seat_number = models.IntegerField(validators=[validators.MinValueValidator(1)])
    screening = models.ForeignKey(
        Screening,
        on_delete=models.CASCADE,
        related_name="seats",
        null=True,
        blank=True,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="seats",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat_number", "screening"],
                name="unique_seat_in_screening",
            )
        ]
        # Ensure that seat numbers are unique within the same row and screening

    def __str__(self):
        return f"Row {self.row}, Seat {self.seat_number}"


class Booking(models.Model):
    screening = models.ForeignKey(
        Screening,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tickets",
    )
    purchase_time = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["screening", "seat"],
                name="unique_ticket_for_seat",
            )
        ]

    def __str__(self):
        return f"Booking for {self.seat} purchased by {self.user} at {self.purchase_time.strftime('%H:%M %d %b %Y')}"
