from django import forms
from .models import Manager, Booking, Membership, Customer

class ManagerForm(forms.ModelForm):
    class Meta:
        model = Manager
        fields = ['email', 'password']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'start_time', 'court', 'manager']

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['member_name', 'status', 'expiration_date']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'booking_history']
