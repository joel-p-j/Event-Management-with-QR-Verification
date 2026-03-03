from django.db import models
from django.conf import settings
from events.models import Event, TicketType
import uuid

class Booking(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    qr_text = models.TextField(null=True, blank=True)
    

    stripe_payment_intent = models.CharField(
        max_length=255, null=True, blank=True
    )
    refunded = models.BooleanField(default=False)


    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.booking_id)
