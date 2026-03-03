from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from .serializers import EventSerializer,TicketTypeSerializer
from .models import Event,TicketType
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from bookings.models import Booking
from django.db.models import Sum
from bookings.serializers import HostBookingSerializer
from rest_framework import status
from rest_framework.permissions import IsAdminUser



# Create your views here.


class EventCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)  
            return Response(serializer.data, status=201)  
        return Response(serializer.errors, status=400)

class EventUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, event_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, host=request.user)
        except Event.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


    def delete(self, request, event_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, host=request.user)
        except Event.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        event.delete()
        return Response({"message": "Event deleted"})
    
    
class EventDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):
        try:
            event = Event.objects.get(
                id=event_id,
                host=request.user
            )
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        event.delete()
        return Response(
            {"detail": "Event deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


    
class EventListView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        
        events = Event.objects.filter(approval_status="approved")
        
        search=request.GET.get('search')
        
        if search:
            events=events.filter(title__icontains=search)
        
        category=request.GET.get('category')
        if category:
            events=events.filter(category__iexact=category)
        
        location=request.GET.get('location')
        if location:
            events=events.filter(location__icontains=location)
        
        sort_by=request.GET.get('sort')
        if sort_by=='price':
            events=events.order_by('price')
        elif sort_by=='-price':
            events=events.order_by('-price')
        
        serializer=EventSerializer(events,many=True,context={"request": request})
        return Response(serializer.data)
    
    
    
class EventDetailView(APIView):
    permission_classes=[AllowAny]
    
    def get(self,request,event_id):
        try:
            event=Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error':'Event not found'})
        
        if event.approval_status != "approved":
            return Response(
                {"error": "Event not approved yet"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer=EventSerializer(event,context={"request": request})
        return Response(serializer.data)
    
    
class MyHostedEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(host=request.user)
        serializer = EventSerializer(events, many=True, context={"request": request})
        return Response(serializer.data)



class TicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_id = request.data.get("event")

        try:
            if request.user.is_staff or request.user.is_superuser:
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, host=request.user)
        except Event.DoesNotExist:
            return Response(
                {"error": "You are not allowed to add tickets to this event"},
                status=403
            )

        serializer = TicketTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    
    
class EventTicketListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, host=request.user)
        except Event.DoesNotExist:
            return Response(
                {"error": "You are not allowed to view tickets"},
                status=403
            )

        tickets = event.ticket_types.all()
        serializer = TicketTypeSerializer(tickets, many=True)
        return Response(serializer.data)




class TicketUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                ticket = TicketType.objects.get(id=ticket_id)
            else:
                ticket = TicketType.objects.get(
                    id=ticket_id,
                    event__host=request.user
                )
        except TicketType.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        serializer = TicketTypeSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)



class TicketDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, ticket_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                ticket = TicketType.objects.get(id=ticket_id)
            else:
                ticket = TicketType.objects.get(
                    id=ticket_id,
                    event__host=request.user
                )
        except TicketType.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        ticket.delete()
        return Response({"message": "Deleted"})




class MyHostedEventsStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(host=request.user)

        response = []

        for event in events:
            total_tickets = (
                TicketType.objects.filter(event=event)
                .aggregate(total=Sum("total_seats"))["total"]
                or 0
            )

            remaining_tickets = (
                TicketType.objects.filter(event=event)
                .aggregate(remaining=Sum("available_seats"))["remaining"]
                or 0
            )

            sold_tickets = total_tickets - remaining_tickets

            revenue = (
                Booking.objects.filter(event=event, status="PAID")
                .aggregate(total=Sum("amount"))["total"]
                or 0
            )

            response.append({
                "event_id": event.id,
                "title": event.title,
                "total_tickets": total_tickets,
                "sold_tickets": sold_tickets,
                "remaining_tickets": remaining_tickets,
                "revenue": revenue,
            })

        return Response(response)




class EventBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        try:
            if request.user.is_staff or request.user.is_superuser:
                event = Event.objects.get(id=event_id)
            else:
                event = Event.objects.get(id=event_id, host=request.user)
        except Event.DoesNotExist:
            return Response(
                {"error": "You are not allowed to view bookings for this event"},
                status=403
            )

        bookings = (
            Booking.objects
            .filter(event=event, status="PAID")
            .select_related("user", "ticket_type")
            .order_by("-created_at")
        )

        serializer = HostBookingSerializer(bookings, many=True)
        return Response(serializer.data)




class AdminApproveEventView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id):
        if not request.user.is_staff:
            return Response(
                {"error": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

        event.approval_status = "approved"
        event.save()

        return Response({"message": "Event approved"})
    


class AdminRejectEventView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id):
        if not request.user.is_staff:
            return Response(
                {"error": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        event.approval_status = "rejected"
        event.save()

        return Response(
            {"message": "Event rejected"},
            status=status.HTTP_200_OK
        )


    
    


class AdminEventListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        events = Event.objects.all().order_by("-created_at")
        serializer = EventSerializer(events, many=True,context={"request": request})
        return Response(serializer.data)





class FixImagePathsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        events = Event.objects.all()
        fixed_count = 0

        for event in events:
            if event.event_image and str(event.event_image).startswith("http://127.0.0.1"):
                fixed_path = str(event.event_image).replace(
                    "http://127.0.0.1:8000/media/",
                    ""
                )
                event.event_image = fixed_path
                event.save()
                fixed_count += 1

        return Response({"message": f"Fixed {fixed_count} images"})