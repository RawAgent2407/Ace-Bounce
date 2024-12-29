from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.ManagerLoginView.as_view(), name='manager_login'),
    path('dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('test/', views.test, name='test'),
    # path('create-booking/', views.CreateBookingView.as_view(), name='create_booking'),
    path('get_manager_id/', views.get_manager_id, name='get_manager_id'),
    path('logout/', views.managerLogoutView, name='logout'),

    path('add_booking/', views.AddBookingView.as_view(), name='add_booking'),
    path('court_booking_details/<int:court_id>/', views.CourtBookingDetailsView.as_view(), name='court_booking_details'),

    path('print_receipt/<int:booking_id>/', views.PrintReceiptView.as_view(), name='print_receipt'),
    path('memberships/', views.MembershipListView.as_view(), name='membership_list'),
    
    path('memberships/add/', views.AddMembershipView.as_view(), name='add_membership'),
    path('memberships/update/<int:barcode_id>/', views.UpdateMembershipView.as_view(), name='update_membership'),
    
    path('memberships/search/', views.SearchMembershipByBarcodeView.as_view(), name='search_membership'),
    path('memberships/get/<int:barcode>/', views.GetMembershipView.as_view(), name='get_membership'),
    path('court-occupancy/', views.CourtOccupancyView.as_view(), name='court_occupancy'),

    path('memberships/delete/<int:barcode_id>/', views.DeleteMembershipView.as_view(), name='delete_membership'),
    path('check-membership/', views.CheckMembershipView.as_view(), name='check_membership'),
    path('add-membership-booking/', views.AddMembershipBookingView.as_view(), name='add_membership_booking'),
    path('membership/get-membership-details/', views.get_membership_details, name='get_membership_details'),

    path('add_advanced_booking/', views.AddAdvancedBookingView.as_view(), name='add_advanced_booking'),
    path('update_status_out/<int:booking_id>/', views.update_status_out, name='update_status_out'),
    # path('add_membership_advanced_booking/<int:phone_number>', views.AddMembershipAdvancedBookingView.as_view(), name='add_membership_advanced_booking'),

    # path('slot_booking/', views.SlotBookingView.as_view(), name='slot_booking'),
    path('confirm_advanced_booking/', views.ConfirmAdvancedBookingView.as_view(), name='confirm_advanced_booking'),
    path('confirm_outadvanced_booking/', views.ConfirmOutSlotBookingView.as_view(), name='confirm_outadvanced_booking'),
    path('m_confirm_advanced_booking/', views.M_ConfirmAdvancedBookingView.as_view(), name='m_confirm_advanced_booking'),
    path('m_outconfirm_advanced_booking/', views.M_OutConfirmAdvancedBookingView.as_view(), name='m_outconfirm_advanced_booking'),

    path('get_booking_details/', views.get_booking_details, name='get_booking_details'),

    
    path('check_barcode/', views.CheckBarcodeView.as_view(), name='check_barcode'),
    path('get_member_data/<int:member_id>/', views.GetMemberDataView.as_view(), name='get_member_data'),
    
    path('add_membership_advanced_booking/', views.AddMembershipAdvancedBookingView.as_view(), name='add_membership_advanced_booking'),
    path('confirm_advanced_membership_booking/', views.ConfirmAdvancedMembershipBookingView.as_view(), name='confirm_advanced_membership_booking'),
    path('search_booking_by_mobile/', views.search_booking_by_mobile, name='search_booking_by_mobile'),
    path('search_booking_by_id/', views.searchBookingByIDView, name='search_booking_by_id'),
    path('search_outbooking_by_id/', views.searchOutBookingByIDView, name='search_outbooking_by_id'),
    path('m_search_booking_by_id/', views.M_SearchBookingByIDView.as_view(), name='m_search_booking_by_id'),
    path('m_outsearch_booking_by_id/', views.M_OutSearchBookingByIDView.as_view(), name='m_outsearch_booking_by_id'),

    
    path('search_membership/', views.SearchMembershipView.as_view(), name='search_membership'),


    path('inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventory/add/', views.AddInventoryView.as_view(), name='add_inventory'),
    path('inventory/update/<int:item_id>/', views.UpdateInventoryView.as_view(), name='update_inventory'),
    path('inventory/delete/<int:item_id>/', views.DeleteInventoryView.as_view(), name='delete_inventory'),


]
