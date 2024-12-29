from django.urls import path
from . import views
from .views import (AdminLoginView, AdminDashboardView, CreateManagerView, ManageManagersView, CreateBookingView, ViewBookingsView, ManageMembershipsView, ViewCustomersView)


urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('create-manager/', CreateManagerView.as_view(), name='create_manager'),
    path('manage-managers/', ManageManagersView.as_view(), name='manage_managers'),
    path('create-booking/', CreateBookingView.as_view(), name='create_booking'),
    path('view-bookings/', ViewBookingsView.as_view(), name='view_bookings'),
    path('manage-memberships/', ManageMembershipsView.as_view(), name='manage_memberships'),
    path('view-customers/', ViewCustomersView.as_view(), name='view_customers'),
    path('get_manager_id/', views.get_manager_id, name='get_manager_id'),
    
    path('filter_memberships/', views.filter_memberships, name='filter_memberships'),
    
    path('filter_customers/', views.filter_customers, name='filter_customers'),
    
    path('filter_member_bookings/', views.filter_member_bookings, name='filter_member_bookings'),
    
    path('filter_transactions/', views.filter_transactions, name='filter_transactions'),
    
    path('logoutadmin/', views.AdminLogoutView, name='adminlogout'),


    
]   