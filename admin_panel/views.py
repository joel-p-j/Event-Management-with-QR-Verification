from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from admin_panel.permissions import IsAdmin
from django.shortcuts import get_object_or_404

from admin_panel.permissions import IsAdmin
from accounts.models import User
from events.models import Event
from bookings.models import Booking


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdmin])
def admin_dashboard(request):
    total_users=User.objects.count()
    total_events=Event.objects.count()
    total_bookings=Booking.objects.count()

    total_revenue=(
        Booking.objects.filter(status='PAID').aggregate(Sum('amount'))["amount__sum"] or 0
    )
    
    return Response({
        'users':total_users,
        'events':total_events,
        'bookings':total_bookings,
        'revenue':total_revenue
    }
        
    )
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdmin])
def admin_all_users(request):
    data=[]
    users=User.objects.all()
    
    for u in users:
        data.append({
            'id':u.id,
            'username':u.username,
            'email':u.email,
            'role':u.role
        })
    return Response(data)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdmin])
def admin_delete_user(request,user_id):
    user=get_object_or_404(User,id=user_id)
    
    if user.role=='admin':
        return Response(
            {
                'error':'Admin user cannot be deleted'
            },status=400
        )
    user.delete()
    return Response({'message':'User deleted'})


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    role = request.data.get("role")

    if role not in ["user", "admin"]:
        return Response({"error": "Invalid role"}, status=400)

    user.role = role
    user.save()

    return Response({"message": "Role updated"})



@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_bookings(request, user_id):
    bookings = Booking.objects.filter(user__id=user_id)

    data = []
    for b in bookings:
        data.append({
            "id": b.booking_id,
            "event": b.event.title,
            "ticket_count": b.quantity,
            "status": b.status,
        })

    return Response(data)
