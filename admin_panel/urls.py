from django.urls import path
from .views import admin_dashboard,admin_all_users,admin_delete_user,admin_update_user_role,admin_user_bookings

urlpatterns=[
    path('dashboard/',admin_dashboard),
    path('users/',admin_all_users),
    path('users/delete/<int:user_id>/',admin_delete_user),
    path('users/update/<int:user_id>/',admin_update_user_role),
    path('users/<int:user_id>/bookings/',admin_user_bookings),
    
]