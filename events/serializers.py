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
    event_image = serializers.SerializerMethodField()
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
            "approval_status",
        ]

    def get_event_image(self, obj):
        request = self.context.get("request")

        if not obj.event_image:
            return None

        # Get raw stored value from DB
        stored_value = str(obj.event_image)

        # If full localhost URL exists, remove it
        if stored_value.startswith("http://127.0.0.1"):
            stored_value = stored_value.replace(
                "http://127.0.0.1:8000",
                ""
            )

        # If full localhost with https somehow
        if stored_value.startswith("https://127.0.0.1"):
            stored_value = stored_value.replace(
                "https://127.0.0.1:8000",
                ""
            )

        # Ensure correct media path format
        if not stored_value.startswith("/media/"):
            if "media/" in stored_value:
                stored_value = "/" + stored_value.split("media/")[-1]
                stored_value = "/media/" + stored_value.split("/media/")[-1]

        # Build absolute production URL
        if request:
            return request.build_absolute_uri(stored_value)

        return stored_value