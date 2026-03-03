from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    EventCreateView,
    EventUpdateView,
    EventListView,
    EventDetailView,
    MyHostedEventsView,
    TicketCreateView,
    EventTicketListView,
    TicketUpdateView,
    TicketDeleteView,
    MyHostedEventsStatsView,
    EventBookingsView,
    EventDeleteView,
    AdminEventListView,
    AdminApproveEventView,
    AdminRejectEventView,
)

urlpatterns = [
    # ================= ADMIN ROUTES (MUST BE FIRST) =================
    path(
        "admin/events/",
        AdminEventListView.as_view()
    ),
    path(
        "admin/events/<int:event_id>/approve/",
        AdminApproveEventView.as_view()
    ),
    path(
        "admin/events/<int:event_id>/reject/",
        AdminRejectEventView.as_view()
    ),

    # ================= HOST / USER ROUTES =================
    path("create/", EventCreateView.as_view()),
    path("my-events/", MyHostedEventsView.as_view()),
    path("update/<int:event_id>/", EventUpdateView.as_view()),
    path("delete/<int:event_id>/", EventDeleteView.as_view()),

    path("tickets/create/", TicketCreateView.as_view()),
    path("tickets/<int:event_id>/", EventTicketListView.as_view()),
    path("tickets/update/<int:ticket_id>/", TicketUpdateView.as_view()),
    path("tickets/delete/<int:ticket_id>/", TicketDeleteView.as_view()),

    path("my-events/stats/", MyHostedEventsStatsView.as_view()),
    path("bookings/<int:event_id>/", EventBookingsView.as_view()),

    # ================= PUBLIC ROUTES =================
    path("", EventListView.as_view()),
    path("<int:event_id>/", EventDetailView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
