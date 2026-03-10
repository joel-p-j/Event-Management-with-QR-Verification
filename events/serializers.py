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

    # writeable field (used when uploading)
    event_image = serializers.ImageField(required=False, allow_null=True)

    # read-only field for frontend display
    event_image_url = serializers.SerializerMethodField(read_only=True)

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
            "event_image_url",
            "ticket_types",
            "host",
            "approval_status",
        ]

    def get_event_image_url(self, obj):
        request = self.context.get("request")

        if not obj.event_image:
            return None

        url = obj.event_image.url

        if request:
            return request.build_absolute_uri(url)

        return url