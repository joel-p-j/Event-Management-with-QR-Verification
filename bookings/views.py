from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from events.models import Event,TicketType
from .models import Booking
from rest_framework.response import Response
from .utils import generate_qr_code, encrypt_data,decrypt_data
from .serializers import BookingHistorySerializer
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from admin_panel.permissions import IsAdmin
from django.db import transaction
from bookings.models import Booking
from bookings.serializers import HostBookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_temp_booking(request):
    user = request.user
    ticket_type_id = request.data.get("ticket_type_id")
    quantity = int(request.data.get("quantity", 0))

    if not ticket_type_id or quantity <= 0:
        return Response(
            {"error": "ticket_type_id and quantity are required"},
            status=400
        )

    try:
        ticket_type = TicketType.objects.get(id=ticket_type_id)
    except TicketType.DoesNotExist:
        return Response({"error": "Ticket type not found"}, status=404)

    if ticket_type.event.approval_status != "approved":
        return Response(
            {"error": "Event not approved yet"},
            status=403
        )

    if ticket_type.available_seats < quantity:
        return Response(
            {"error": "Not enough seats available"},
            status=400
        )


    total_amount = ticket_type.price * quantity

    booking = Booking.objects.create(
        user=user,
        event=ticket_type.event,
        ticket_type=ticket_type,
        quantity=quantity,
        amount=total_amount,
        status="PENDING"
    )

    return Response(
        {
            "booking_id": str(booking.booking_id),
            "amount": total_amount
        },
        status=201
    )

    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_qr(request):
    user = request.user
    scanned_text = request.data.get("qr_text")

    if not scanned_text:
        return Response({"status": "invalid"}, status=400)

    # 🔐 Decrypt QR
    try:
        decrypted = decrypt_data(scanned_text.strip())
        booking_id, user_id = decrypted.split(":")
    except Exception as e:
        print("QR decrypt error:", e)
        return Response({"status": "invalid"}, status=400)

    try:
        booking = Booking.objects.select_related(
            "event", "ticket_type", "user"
        ).get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return Response({"status": "invalid"}, status=404)

    if booking.status != "PAID":
        return Response({"status": "not_paid"}, status=200)

    if booking.used:
        return Response({"status": "already_used"}, status=200)

    
    event_id = request.data.get("event_id")

    if not event_id:
        return Response({"status": "invalid_event"}, status=400)

    try:
        booking = Booking.objects.select_related(
            "event", "ticket_type", "user"
        ).get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return Response({"status": "invalid"}, status=404)

    if str(booking.event.id) != str(event_id):
        return Response(
            {"status": "wrong_event"},
            status=200
        )

    

    if user.is_staff or user.is_superuser:
        pass

    elif booking.event.host == user:
        pass

    elif str(booking.user.id) == str(user_id):
        pass

    else:
        return Response({"status": "not_allowed"}, status=403)

    booking.used = True
    booking.save(update_fields=["used"])

    return Response(
        {
            "status": "valid",
            "event": booking.event.title,
            "user": booking.user.email,
            "ticket_type": booking.ticket_type.name,
            "quantity": booking.quantity,
        },
        status=200
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_status(request, booking_id):
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id,
        user=request.user
    )
    return Response({"status": booking.status})





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_history(request):
    user=request.user
    
    bookings = Booking.objects.filter(
        user=request.user,
        status="PAID"
    ).order_by("-created_at")
    
    serializer=BookingHistorySerializer(bookings,many=True, context={'request': request})
    return Response(serializer.data)


stripe.api_key=settings.STRIPE_SECRET_KEY



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    booking_id = request.data.get("booking_id")

    booking = Booking.objects.get(
        booking_id=booking_id,
        user=request.user,
        status="PENDING"
    )

    intent = stripe.PaymentIntent.create(
        amount=int(booking.amount * 100),
        currency='inr',
        automatic_payment_methods={
            "enabled": True,   # 🔥 Enables UPI, GPay, etc
        },
        metadata={
            "booking_id": str(booking.booking_id)
        }
    )

    booking.stripe_payment_intent = intent.id
    booking.save()

    return Response({
        "client_secret": intent.client_secret
    })

    




@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    event_type = event["type"]
    intent = event["data"]["object"]

   
    if event_type == "payment_intent.succeeded":
        booking_id = intent["metadata"].get("booking_id")

        try:
            booking = Booking.objects.select_related("ticket_type").get(
                booking_id=booking_id
            )
        except Booking.DoesNotExist:
            return HttpResponse(status=200)

        # 🔐 Idempotency
        if booking.status == "PAID":
            return HttpResponse(status=200)

        ticket_type = booking.ticket_type

        if ticket_type.available_seats < booking.quantity:
            booking.status = "CANCELLED"
            booking.save()
            return HttpResponse(status=200)

        ticket_type.available_seats -= booking.quantity
        ticket_type.save()

        booking.status = "PAID"
        booking.stripe_payment_intent = intent["id"]

        plain_text = f"{booking.booking_id}:{booking.user.id}"
        encrypted_text = encrypt_data(plain_text)
        booking.qr_text = encrypted_text

        qr_image = generate_qr_code(encrypted_text)
        booking.qr_code.save("qr.png", qr_image)

        booking.save()

        print("✅ PAYMENT SUCCESS - SEATS CONFIRMED")


    return HttpResponse(status=200)







@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_all_bookings(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Not allowed"}, status=403)

    bookings = (
        Booking.objects
        .select_related("user", "event", "ticket_type")
        .order_by("-created_at")
    )

    data = []
    for b in bookings:
        data.append({
            "booking_id": str(b.booking_id),   
            "user": b.user.email,
            "event": b.event.title,
            "ticket_count": b.quantity,
            "amount": b.amount,
            "status": b.status,
        })

    return Response(data)






@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if booking.status != "PAID":
        return Response({"error": "Only PAID bookings can be cancelled"}, status=400)

    # restore seats
    ticket = booking.ticket_type
    ticket.available_seats += booking.quantity
    ticket.save()

    booking.status = "CANCELLED"
    booking.save()

    return Response({"message": "Booking cancelled"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    status = request.data.get("status")

    if status not in ["PAID", "CANCELLED"]:
        return Response({"error": "Invalid status"}, status=400)

    # restore seats if cancelling
    if status == "CANCELLED" and booking.status == "PAID":
        ticket = booking.ticket_type
        ticket.available_seats += booking.quantity
        ticket.save()

    booking.status = status
    booking.save()

    return Response({"message": "Status updated"})




class EventBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        if request.user.is_staff or request.user.is_superuser:
            event = get_object_or_404(Event, id=event_id)
        else:
            event = get_object_or_404(Event, id=event_id, host=request.user)

        bookings = (
            Booking.objects
            .filter(event=event, status="PAID")
            .select_related("user", "ticket_type")
            .order_by("-created_at")
        )

        serializer = HostBookingSerializer(bookings, many=True)
        return Response(serializer.data)




@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def refund_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if booking.refunded or booking.status != "PAID":
        return Response({"error": "Invalid refund"}, status=400)

    stripe.Refund.create(
        payment_intent=booking.stripe_payment_intent
    )

    booking.refunded = True
    booking.status = "CANCELLED"

    ticket = booking.ticket_type
    ticket.available_seats += booking.quantity
    ticket.save()

    booking.save()

    return Response({"message": "Refund successful"})




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_booking_for_payment(request, booking_id):
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id,
        user=request.user,
        status="PENDING"
    )

    return Response({
        "booking_id": str(booking.booking_id),
        "event": booking.event.title,
        "ticket_type": booking.ticket_type.name,
        "quantity": booking.quantity,
        "amount": booking.amount,
    })