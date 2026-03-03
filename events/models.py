from django.db import models
from django.conf import settings

class Event(models.Model):

    User = settings.AUTH_USER_MODEL

    CATEGORY_CHOICES = (
        ('music', 'MUSIC'),
        ('comedy', 'COMEDY'),
        ('tech', 'TECH'),
        ('dance', 'DANCE'),
        ('sports', 'SPORTS'),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hosted_events"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    event_image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='music')

    approval_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class TicketType(models.Model):
    event=models.ForeignKey(Event,related_name='ticket_types',on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=8,decimal_places=2)
    total_seats=models.PositiveIntegerField()
    available_seats=models.PositiveIntegerField()
    priority = models.PositiveIntegerField(
        help_text="Lower number = higher priority"
    )
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"
    
