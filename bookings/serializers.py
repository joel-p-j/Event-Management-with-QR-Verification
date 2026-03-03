from rest_framework import serializers
from .models import  Booking

from rest_framework import serializers
from .models import Booking


class BookingHistorySerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(
        source="event.title",
        read_only=True
    )

    event_date = serializers.DateTimeField(
        source="event.date",
        read_only=True
    )

    event_image = serializers.ImageField(
        source="event.event_image",
        read_only=True
    )

    ticket_type_name = serializers.CharField(
        source="ticket_type.name",
        read_only=True
    )

    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "event_name",
            "event_date",
            "event_image",
            "ticket_type_name",
            "quantity",
            "amount",
            "status",
            "qr_code_url",
            "created_at",
        ]

    def get_qr_code_url(self, obj):
        request = self.context.get("request")
        if obj.qr_code:
            return request.build_absolute_uri(obj.qr_code.url)
        return None

    
    

class HostBookingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email")
    ticket_type = serializers.CharField(source="ticket_type.name")
    qr_status = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "user_email",
            "ticket_type",
            "quantity",
            "amount",
            "qr_status",
            "created_at",
        ]

    def get_qr_status(self, obj):
        if obj.used:
            return "USED"
        if obj.status == "PAID":
            return "ACTIVE"
        return "INVALID"