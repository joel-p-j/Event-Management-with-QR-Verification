from django.urls import path
from .views import create_temp_booking,verify_qr,booking_history,create_payment_intent,stripe_webhook,admin_all_bookings,admin_cancel_booking,EventBookingsView,admin_update_booking_status,get_booking_for_payment,booking_status

urlpatterns=[
    path('create-temp/',create_temp_booking),
    path('verify-qr/',verify_qr),
    path("history/", booking_history),
    path('create-payment-intent/',create_payment_intent),
    path("stripe-webhook/", stripe_webhook),
    path("bookings/<int:event_id>/", EventBookingsView.as_view()),
    path("admin/update/<uuid:booking_id>/", admin_update_booking_status),
    path("status/<uuid:booking_id>/", booking_status),


    path("payment/<uuid:booking_id>/", get_booking_for_payment),
    
    path("admin/all/", admin_all_bookings),
    path("admin/cancel/<uuid:booking_id>/", admin_cancel_booking),

]