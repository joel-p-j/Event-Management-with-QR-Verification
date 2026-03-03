from rest_framework import serializers
from .models import Event, TicketType


class TicketTypeSerializer(serializers.ModelSerializer):
    priority = serializers.IntegerField(required=False, default=1)

    class Meta:
        model = TicketType
        fields = [
            "id",
            "name",
            "price",
            "total_seats",
            "available_seats",
            "priority",
        ]

    def validate(self, data):
        total = data.get("total_seats")
        available = data.get("available_seats")

        if available > total:
            raise serializers.ValidationError(
                "Available seats cannot exceed total seats."
            )

        return data


class EventSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source="host.id")
    event_image = serializers.ImageField(required=False)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    approval_status = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "location",
            "category",
            "event_image",
            "ticket_types",
            "host",
            "approval_status"
        ]
