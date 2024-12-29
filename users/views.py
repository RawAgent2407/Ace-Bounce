from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import *
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.views import View
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import check_password
from .models import Admin, Manager, Membership, Booking, Customer, Court, Membership_Plan, MembershipBooking, slot
from .forms import ManagerForm, BookingForm, MembershipForm, CustomerForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date
from django.shortcuts import render, redirect
from django.views import View
from .models import Booking, Court
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from .models import Membership, MembershipBooking
from datetime import datetime, timedelta
from .utils import book_court_with_thread
from datetime import datetime
from pytz import timezone as pytz_timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date, parse_time

# import timezones
from django.utils import timezone


class AdminLoginView(View):
	def get(self, request):
		token = request.COOKIES.get('session_id')
		print(token)
		if token:
			try:
				session = Session.objects.get(session_key=token)
				session_data = session.get_decoded()
				user_id = session_data.get('Admin_Session')
				if user_id:
					user = Admin.objects.filter(id=user_id).first()
					if user:
						return redirect('/admin/dashboard')
			except Session.DoesNotExist:
				pass
		return render(request, 'admin_login.html')

	def post(self, request):
		email = request.POST['email']
		password = request.POST['password']
		user = Admin.objects.filter(email=email).first()
		print(user)
		if user and check_password(password, user.password):
			request.session['Admin_Session'] = user.id
			return redirect('/admin/dashboard')
		return render(request, 'admin_login.html', {'error': 'Invalid email or password'})


class AdminDashboardView(View):
	def get(self, request):
		token = request.COOKIES.get('session_id')
		print(token)
		if token:
			try:
				session = Session.objects.get(session_key=token)
				session_data = session.get_decoded()
				user_id = session_data.get('Admin_Session')
				if user_id:
					user = Admin.objects.filter(id=user_id).first()
					membership = Membership.objects.all()
					yesterday_membership = Membership.objects.filter(created_at=datetime.now().date() - timedelta(days=1))
					lastweek_membership = Membership.objects.filter(created_at__gte=datetime.now().date() - timedelta(days=7))
					thismonth_membership = Membership.objects.filter(created_at__gte=datetime.now().date() - timedelta(days=30))

					court_1 = Booking.objects.filter(court=1)
					m_court_1 = MembershipBooking.objects.filter(court=1)

					court_one = len(court_1) + len(m_court_1)

					court_2 = Booking.objects.filter(court=2)
					m_court_2 = MembershipBooking.objects.filter(court=2)

					court_two = len(court_2) + len(m_court_2)

					court_3 = Booking.objects.filter(court=3)
					m_court_3 = MembershipBooking.objects.filter(court=3)

					court_three = len(court_3) + len(m_court_3)

					court_4 = Booking.objects.filter(court=4)
					m_court_4 = MembershipBooking.objects.filter(court=4)

					court_four = len(court_4) + len(m_court_4)

					court_5 = Booking.objects.filter(court=5)
					m_court_5 = MembershipBooking.objects.filter(court=5)

					court_five = len(court_5) + len(m_court_5)

					todays_customer_ammount = sum([membership.amount for membership in Booking.objects.filter(date=datetime.now().date())])

					thismonth_customer_ammount = sum([membership.amount for membership in Booking.objects.filter(date__gte=datetime.now().date() - timedelta(days=30))])

					todays_membership_amount = sum([membership.plan.amount for membership in Membership.objects.filter(created_at=datetime.now().date())])

					thismonth_membership_amount = sum([membership.plan.amount for membership in Membership.objects.filter(created_at__gte=datetime.now().date() - timedelta(days=30))])

					total_todays_collections = todays_customer_ammount + todays_membership_amount

					total_thismonth_collections = thismonth_customer_ammount + thismonth_membership_amount
					manager = Manager.objects.all()

					today_booking_slot = Booking.objects.filter(date=datetime.now().date()).count()
					today_membership_slot = MembershipBooking.objects.filter(booking_date=datetime.now().date()).count()

					todays_total_slot = today_booking_slot + today_membership_slot

					thismounth_booking_slot = Booking.objects.filter(date__gte=datetime.now().date() - timedelta(days=30)).count()

					thismonth_membership_slot = MembershipBooking.objects.filter(booking_date__gte=datetime.now().date() - timedelta(days=30)).count()

					total_thismonth_slot = thismounth_booking_slot + thismonth_membership_slot

					package = Membership_Plan.objects.all()

					if user:
						return render(request, 'admin_dashboard.html',
						              {'user': user, 'memberships': membership, 'yesterday_membership': yesterday_membership, 'lastweek_membership': lastweek_membership,
						               'thismonth_membership': thismonth_membership, 'managers': manager, 'court_one': court_one, 'court_two': court_two, 'court_three': court_three,
						               'court_four': court_four, 'court_five': court_five, 'todays_customer_ammount': todays_customer_ammount, 'todays_membership_amount': todays_membership_amount,
						               'total_todays_collections': total_todays_collections, 'thismonth_customer_ammount': thismonth_customer_ammount,
						               'thismonth_membership_amount': thismonth_membership_amount, 'total_thismonth_collections': total_thismonth_collections, 'today_booking_slot': today_booking_slot,
						               'today_membership_slot': today_membership_slot, 'todays_total_slot': todays_total_slot, 'thismounth_booking_slot': thismounth_booking_slot,
						               'thismonth_membership_slot': thismonth_membership_slot, 'total_thismonth_slot': total_thismonth_slot, 'packages': package})
			except Session.DoesNotExist:
				redirect('/admin/login')
		return redirect('/admin/login')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.utils.timezone import now
import json


@csrf_exempt
def filter_memberships(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		filter_type = data.get('filter')
		start_date = data.get('start_date')
		end_date = data.get('end_date')

		memberships = Membership.objects.all()
		if filter_type == 'day':
			memberships = memberships.filter(created_at=now().date() - timedelta(days=1))
		elif filter_type == 'week':
			memberships = memberships.filter(created_at__gte=now().date() - timedelta(days=7))
		elif filter_type == 'month':
			memberships = memberships.filter(created_at__gte=now().date() - timedelta(days=30))
		elif filter_type == 'custom':
			if start_date and end_date:
				memberships = memberships.filter(created_at__range=[start_date, end_date])

		memberships_data = list(memberships.values('barcode', 'id', 'member_name', 'mobile_number', 'email', 'manager__name', 'created_at', 'expiration_date', 'status', 'plan__name'))
		print("BOOking: ", memberships_data)
		return JsonResponse(memberships_data, safe=False)

@csrf_exempt
def filter_member_bookings(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		filter_type = data.get('filter')
		start_date = data.get('start_date')
		end_date = data.get('end_date')

		mem_bookings = MembershipBooking.objects.all()
		print("M: ",mem_bookings)
		if filter_type == 'day':
			mem_bookings = mem_bookings.filter(booking_date=now().date() - timedelta(days=1))
		elif filter_type == 'week':
			mem_bookings = mem_bookings.filter(booking_date__gte=now().date() - timedelta(days=7))
		elif filter_type == 'month':
			mem_bookings = mem_bookings.filter(booking_date__gte=now().date() - timedelta(days=30))
		elif filter_type == 'custom':
			if start_date and end_date:
				mem_bookings = mem_bookings.filter(booking_date__range=[start_date, end_date])
		# print(mem_bookings)
		mem_bookings_data = list(mem_bookings.values(
			'id',
			'membership__barcode',
			'membership__id',
			'booking_date',
			'start_time',
			'slots__number',
			'manager__name'
		))
		print("DA ", mem_bookings_data)
		return JsonResponse(mem_bookings_data, safe=False)




def filter_customers(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		filter_type = data.get('filter')
		start_date = data.get('start_date')
		end_date = data.get('end_date')

		# Assuming you have a created_at field to filter by
		customers = Booking.objects.all()
		if filter_type == 'day':
			customers = customers.filter(date=now().date() - timedelta(days=1))
		elif filter_type == 'week':
			customers = customers.filter(date__gte=now().date() - timedelta(days=7))
		elif filter_type == 'month':
			customers = customers.filter(date__gte=now().date() - timedelta(days=30))
		elif filter_type == 'custom':
			if start_date and end_date:
				customers = customers.filter(date__range=[start_date, end_date])
		else:
			customers = Customer.objects.all()

		customers_data = list(customers.values(
			'id',
			'name',
			'email',
			'mobile_number',
			'date',
			'start_time',
			'slots__number',
			'amount',
			'payment_method',
			'manager__name',
			'discount'
		))

		return JsonResponse(customers_data, safe=False)



def filter_transactions(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		filter_type = data.get('filter', 'all')
		start_date = data.get('start_date')
		end_date = data.get('end_date')
		customer_type = data.get('customer_type', 'all')

		transactions = []

		if customer_type == 'one-time':
			bookings = Booking.objects.all()
			if filter_type == 'day':
				bookings = bookings.filter(date=now().date() - timedelta(days=1))
			elif filter_type == 'week':
				bookings = bookings.filter(date__gte=now().date() - timedelta(days=7))
			elif filter_type == 'month':
				bookings = bookings.filter(date__gte=now().date() - timedelta(days=30))
			elif filter_type == 'custom':
				if start_date and end_date:
					bookings = bookings.filter(date__range=[start_date, end_date])
			transactions = bookings.values('id', 'name', 'email', 'mobile_number', 'date', 'amount')

		elif customer_type == 'members':
			memberships = MembershipBooking.objects.all()
			print(memberships)
			if filter_type == 'day':
				memberships = memberships.filter(created_at=now().date() - timedelta(days=1))
			elif filter_type == 'week':
				memberships = memberships.filter(created_at__gte=now().date() - timedelta(days=7))
			elif filter_type == 'month':
				memberships = memberships.filter(created_at__gte=now().date() - timedelta(days=30))
			elif filter_type == 'custom':
				if start_date and end_date:
					memberships = memberships.filter(created_at__range=[start_date, end_date])
			print(transactions)
			transactions = memberships.values('id', 'membership', 'booking_date')
			print(memberships)

		return JsonResponse(list(transactions), safe=False)


class ManagerLoginView(View):
	def get(self, request):
		token = request.COOKIES.get('session_id')
		if token:
			try:
				session = Session.objects.get(session_key=token)
				session_data = session.get_decoded()
				user_id = session_data.get('Manager_Session')
				if user_id:
					user = Manager.objects.filter(id=user_id).first()
					if user:
						return render(request, 'manager_dashboard.html')
			except Session.DoesNotExist:
				pass
		return render(request, 'manager_login.html')

	@csrf_exempt
	def post(self, request):
		email = request.POST['email']
		password = request.POST['password']
		user = Manager.objects.filter(email=email).first()
		if user and check_password(password, user.password):
			request.session['Manager_Session'] = user.id
			return redirect('/manager/dashboard')
		return render(request, 'manager_login.html', {'error': 'Invalid email or password'})


class ManagerDashboardView(View):
	def get(self, request):
		token = request.COOKIES.get('session_id')
		if token:
			try:
				session = Session.objects.get(session_key=token)
				session_data = session.get_decoded()
				user_id = session_data.get('Manager_Session')
				if user_id:
					user = Manager.objects.filter(id=user_id).first()
					if user:
						currunt_date = datetime.now().date()
						print(currunt_date)
						Booked = Booking.objects.filter(manager=user, advanced_booked=False, date=currunt_date)

						Member_Booked = MembershipBooking.objects.filter(manager=user, advanced_booked=False, booking_date=currunt_date)

						todays_booking_count = Booked.count() + Member_Booked.count()

						occupied_court = Court.objects.filter(booked=True)

						courts_all = Court.objects.all()

						todays_membership = Membership.objects.filter(manager=user, created_at=currunt_date)

						todays_membership_count = Membership.objects.filter(manager=user, created_at=currunt_date).count()

						todays_collection = sum([membership.plan.amount for membership in todays_membership])

						todays_booking = sum([booking.amount for booking in Booked])

						todays_disc_collection = sum([membership.plan.discount_percentage for membership in todays_membership])

						todays_disc_booking = sum([booking.discount for booking in Booked])

						today_manager_collection = todays_collection + todays_booking
						today_disc_total = todays_disc_booking + todays_disc_collection

						print("Amount: ", today_manager_collection)
						print("Discount: ", today_disc_total)

						print(Booked)
						advanced_booked = Booking.objects.filter(manager=user, advanced_booked=True, date__gte=currunt_date)

						advanced_membership_booked = MembershipBooking.objects.filter(advanced_booked=True, booking_date__gte=currunt_date)

						plans = Membership_Plan.objects.all()
						membership = Membership.objects.all()
						slots = slot.objects.all()
						courts = Court.objects.all()

						try:
							rackets = Inventory.objects.get(item_name__iexact='racket')
						except Inventory.DoesNotExist:
							rackets = 0

						try:
							# balls = 0
							balls = Inventory.objects.get(item_name__iexact='ball')
							print("BII ", balls)
							if not balls:
								balls = 0

						except Inventory.DoesNotExist:
							balls = 0
						except ObjectDoesNotExist:
							balls = 0

						occupied_ball = sum([booking.inventory_ball for booking in Booking.objects.filter(manager=user)])
						print("Occupied: ", occupied_ball)
						if rackets and rackets.quantity >= 2:
							occupied_racket = len(occupied_court) * 2
						else:
							occupied_racket = 0

						expired_memberships = Membership.objects.filter(expiration_date__lt=currunt_date)
						court_status = {court.id: court.booked for court in courts_all}

						upcoming_expiry_date = currunt_date + timedelta(days=7)

						expiring_memberships = Membership.objects.filter(expiration_date__gte=currunt_date, expiration_date__lte=upcoming_expiry_date)

						expiring_memberships = [
							{
								'membership': membership,
								'remaining_days': (membership.expiration_date - currunt_date).days
							}
							for membership in expiring_memberships
						]

						context = {
							'booked': Booked,
							'advanced_booked': advanced_booked,
							'advanced_membership_booked': advanced_membership_booked,
							'plans': plans,
							'membership': membership,
							'slots': slots,
							'courts': courts,
							'todays_membership': todays_membership,
							'courts_all': courts_all,
							'user': user,
							'Member_Booked': Member_Booked,
							'expired_memberships': expired_memberships,
							'expiring_memberships': expiring_memberships,
							'today_disc_total': today_disc_total,
							'today_manager_collection': today_manager_collection,
							'todays_membership_count': todays_membership_count,
							'todays_booking_count': todays_booking_count,
							'court_status': court_status,
							'rackets': rackets,
							'balls': balls,
							'occupied_racket': occupied_racket,
							'occupied_ball': occupied_ball,
						}

						return render(request, 'manager_dashboard.html', context)

			except Session.DoesNotExist:
				return redirect('/manager/login')

		return redirect('/manager/login')


class CourtOccupancyView(View):
	def get(self, request):
		courts = Court.objects.all()
		court_status = {court.id: court.booked for court in courts}
		return JsonResponse(court_status)


def get_manager_id(request):
	session_id = request.COOKIES.get('session_id')
	try:
		session = Session.objects.get(session_key=session_id)
		session_data = session.get_decoded()
		manager_id = session_data.get('Manager_Session')
		if manager_id:
			return JsonResponse({'manager_id': manager_id})
	except Session.DoesNotExist:
		pass
	return JsonResponse({'error': 'Admin ID not found'}, status=400)


# class managerLogoutView(View):
#     def post(self, request):
#         cookie = request.COOKIES.get('session_id')

#         # Delete the session if the cookie exists
#         if cookie:
#             try:
#                 session = Session.objects.get(session_key=cookie)
#                 session.delete()
#             except Session.DoesNotExist:
#                 pass
#         return redirect('/manager/login/')
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.urls import reverse


def managerLogoutView(request):
	logout(request)
	return redirect('/manager/login')


def AdminLogoutView(request):
	logout(request)
	return redirect('/admin/login')


class CreateManagerView(View):
	def get(self, request):
		form = ManagerForm()
		return render(request, 'create_manager.html', {'form': form})

	def post(self, request):
		form = ManagerForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/admin/manage-managers')
		return render(request, 'create_manager.html', {'form': form})


class CreateBookingView(View):
	def get(self, request):
		token = request.COOKIES.get('session_id')
		if token:
			try:
				session = Session.objects.get(session_key=token)
				session_data = session.get_decoded()
				user_id = session_data.get('Manager_Session')
				if user_id:
					return render(request, 'create_booking.html')
			except Session.DoesNotExist:
				return redirect('/manager/login')
		return redirect('/manager/login')

	def post(self, request):
		date = request.POST['date']
		time = request.POST['time']
		court = request.POST['court']
		manager_id = request.POST['manager_id']
		manager = Manager.objects.get(id=manager_id)
		Booking.objects.create(date=date, time=time, court=court, manager=manager)
		return JsonResponse({'message': 'Booking created successfully'})


class ViewBookingsView(View):
	def get(self, request):
		today = date.today()
		live_bookings = Booking.objects.filter(date=today)
		today_bookings = Booking.objects.filter(date=today)
		upcoming_bookings = Booking.objects.filter(date__gt=today)
		context = {
			'live_bookings': live_bookings,
			'today_bookings': today_bookings,
			'upcoming_bookings': upcoming_bookings
		}
		return render(request, 'view_bookings.html', context)


from datetime import datetime, timedelta
from django.utils.timezone import make_aware
import pytz


class AddBookingView(View):
	def get(self, request):
		courts = Court.objects.all()
		slots = slot.objects.all()
		return render(request, 'add_booking.html', {'courts': courts, 'slots': slots})

	def post(self, request):
		name = request.POST['add_booking_name_test']
		email_id = request.POST['add_booking_email']
		mobile_number = request.POST['add_booking_mobile_number']
		date = request.POST['add_booking_date']
		start_time = request.POST['add_booking_start_time']
		s = request.POST['add_booking_slots']
		inventory_ball = request.POST['inventory_ball']
		print(inventory_ball)
		inventory_racket = request.POST['inventory_racket']
		print(inventory_racket)

		slots = slot.objects.get(id=s)
		end_time = request.POST['add_booking_end_time']
		amount = slots.amount
		# payment_method = request.POST['add_booking_payment_method']
		manager_id = request.COOKIES.get('session_id')
		session_data = Session.objects.get(session_key=manager_id).get_decoded()
		manager_id = session_data.get('Manager_Session')
		manager = Manager.objects.get(id=manager_id)
		# discount = request.POST['advanced_normal_discount']
		# amount = amount - discount
		# print(amount)
		court_number = request.POST['add_booking_court']
		court = Court.objects.get(court_number=court_number)
		# inventory_ball = Inventory.objects.get(id=1)
		# inventory_racket = Inventory.objects.get(id=2)

		# Convert times to datetime objects
		start_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
		end_datetime = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')

		# Adjust end_datetime if it falls on the next day
		if end_datetime <= start_datetime:
			end_datetime += timedelta(days=1)

		# Check for existing bookings
		if Booking.objects.filter(court=court, date=date, start_time__lt=end_datetime, end_time__gt=start_datetime).exists():
			# return redirect('/manager/dashboard/')
			return JsonResponse({'status': 'occupied'})

		# Handle discount notification
		# if int(discount) > 1:
		#     subject = 'Discount Offered'
		#     message = render_to_string('registration/discount.html', {'discount': discount, 'manager': manager, 'email': email_id})
		#     from_email = settings.DEFAULT_FROM_EMAIL
		#     recipient_list = ['info@nuviontech.com']
		#     email = EmailMessage(subject, message, from_email, recipient_list)
		#     email.content_subtype = 'html'
		#     email.send()

		# Make datetime objects timezone-aware
		kolkata_tz = pytz.timezone('Asia/Kolkata')
		aware_start_time = make_aware(start_datetime, timezone=kolkata_tz)
		aware_end_time = make_aware(end_datetime, timezone=kolkata_tz)

		# Create booking
		booking = Booking.objects.create(
			name=name,
			email=email_id,
			mobile_number=mobile_number,
			date=date,
			start_time=aware_start_time,
			end_time=aware_end_time,
			slots=slots,
			# payment_method=payment_method,
			manager=manager,
			court=court,
			# discount=discount,
			amount=amount,
			inventory_ball=inventory_ball,
			inventory_racket=inventory_racket
		)

		# Update court status
		court.booked = True
		court.save()

		# Start thread to update court status
		# book_court_with_thread(court.id, aware_end_time)

		return redirect(f'/manager/dashboard/')


class CourtBookingDetailsView(View):
	def get(self, request, court_id):
		court = get_object_or_404(Court, id=court_id)
		bookings = Booking.objects.filter(court=court)
		return render(request, 'court_booking_details.html', {'bookings': bookings, 'court': court})


class AddMembershipView(View):
	def get(self, request):
		plans = Membership_Plan.objects.all()

		return render(request, 'add_membership.html', {'plans': plans})

	def post(self, request):
		print(request.POST)
		barcode = request.POST['barcode']
		print(barcode)
		member_name = request.POST['uniqueMemberName']
		print(member_name)
		mobile_number = request.POST['uniqueMobileNumber']
		email = request.POST['uniqueEmail']
		if Membership.objects.filter(email=email).exists():
			return render(request, 'add_membership.html', {'error': 'Email already exists'})
		# hours_remaining = request.POST['hours_remaining']
		hours_remaining = 0
		expiration_date = request.POST['uniqueExpirationDate']
		expiration_date = datetime.strptime(expiration_date, '%m/%d/%Y').strftime('%d/%m/%Y')

		print(expiration_date)
		payment_method = request.POST['uniquePaymentMethod']
		status = request.POST['uniqueStatus']
		manager_id = request.COOKIES.get('session_id')
		session_data = Session.objects.get(session_key=manager_id).get_decoded()
		manager_id = session_data.get('Manager_Session')
		manager = Manager.objects.get(id=manager_id)
		plan = request.POST['uniquePlan']
		plans = Membership_Plan.objects.get(id=plan)
		hours_remaining = plans.Total_hours + hours_remaining
		print(plan)
		print(plans)

		if Membership.objects.filter(barcode=barcode).exists():
			print("Barcode already exists")

		Membership.objects.create(
			member_name=member_name, mobile_number=mobile_number, email=email,
			hours_remaining=hours_remaining, expiration_date=expiration_date,
			payment_method=payment_method, status=status, manager=manager, barcode=barcode, plan=plans,
			created_at=now().date()
		)
		return redirect('/manager/dashboard')


class MembershipListView(View):
	def get(self, request):
		memberships = Membership.objects.all()

		return render(request, 'membership_list.html', {'memberships': memberships})


class UpdateMembershipView(View):
	def get(self, request, barcode_id):
		membership = get_object_or_404(Membership, barcode=barcode_id)
		return render(request, 'update_membership.html', {'membership': membership})

	def post(self, request, barcode_id):
		print(request.POST)
		expiration_date_update = request.POST['uniqueExpirationDate']
		expiration_date = datetime.strptime(expiration_date_update, '%m/%d/%Y').strftime('%Y-%m-%d')
		membership = get_object_or_404(Membership, barcode=barcode_id)
		membership.member_name = request.POST['uniqueMemberName']
		membership.mobile_number = request.POST['uniqueMobileNumber']
		membership.email = request.POST['uniqueEmail']
		membership.hours_remaining = request.POST['uniqueHoursRemaining']
		membership.expiration_date = expiration_date
		membership.payment_method = request.POST['uniquePlan']
		membership.status = request.POST['uniqueStatus']
		membership.amount = request.POST['uniqueAmount']
		membership.discount = request.POST['uniqueDiscount']
		membership.amount = int(membership.amount) - int(membership.discount)
		print(membership.amount)
		membership.save()
		return redirect('/manager/dashboard/')


class DeleteMembershipView(View):
	def get(self, request, barcode_id):
		membership = get_object_or_404(Membership, id=barcode_id)
		membership.delete()
		return redirect('/manager/dashboard/')


class CheckMembershipView(View):
	def post(self, request):
		barcode = request.POST.get('barcode')
		try:
			membership = Membership.objects.get(barcode=barcode, status='Active')
			# if membership.hours_remaining > 0:
			#     return JsonResponse({'status': 'exists', 'barcode': membership.barcode})
			# else:
			#     return JsonResponse({'status': 'no_hours'})
			if membership:
				return JsonResponse({'status': 'exists', 'barcode': membership.barcode})
		except Membership.DoesNotExist:
			return JsonResponse({'status': 'not_exists'})


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import Membership, slot, Court, Booking, MembershipBooking, Inventory, Manager
from django.utils.dateparse import parse_date
from django.contrib.sessions.models import Session
import logging
from datetime import datetime
from django.utils.timezone import make_aware
from pytz import timezone as pytz_timezone


class AddMembershipBookingView(View):

	def get(self, request):
		slots = slot.objects.all()
		courts = Court.objects.all()
		return render(request, 'add_membership_booking.html', {'courts': courts, 'slots': slots})

	@csrf_exempt
	def post(self, request):
		try:
			import logging
			logging.basicConfig(level=logging.DEBUG)
			print(request.POST)
			barcode_id = request.POST.get('membership_barcode')
			membership = get_object_or_404(Membership, barcode=barcode_id)
			slots = int(request.POST.get('slots_membership_booking'))
			s = slot.objects.get(number=slots)
			booking_date = parse_date(request.POST.get('booking_date'))
			start_time = request.POST['start_time']
			end_time = request.POST['end_time_membership_booking']

			if booking_date is None or start_time is None or end_time is None:
				raise ValueError("Invalid date or time format.")

			if membership.hours_remaining < slots:
				plans = Membership_Plan.objects.all()
				return render(request, 'add_membership.html', {'plans': plans})
			# 	return HttpResponse("Not enough hours remaining in the membership.", status=400)

			membership.hours_remaining -= slots
			membership.save()

			manager_session_key = request.COOKIES.get('session_id')
			session_data = Session.objects.get(session_key=manager_session_key).get_decoded()
			manager_id = session_data.get('Manager_Session')
			manager = get_object_or_404(Manager, id=manager_id)
			court_number = request.POST['court']
			court = Court.objects.get(court_number=court_number)

			if Booking.objects.filter(court=court, date=booking_date, start_time__lt=start_time, end_time__gt=start_time).exists():
				return JsonResponse({'status': 'error', 'message': 'Court already booked for the selected time.'})

			if MembershipBooking.objects.filter(membership=membership, booking_date=booking_date, start_time=start_time).exists():
				return JsonResponse({'status': 'error', 'message': 'Membership already booked for the selected time.'})

			naive_start_time = datetime.strptime(f"{booking_date} {start_time}", '%Y-%m-%d %H:%M')
			naive_end_time = datetime.strptime(f"{booking_date} {end_time}", '%Y-%m-%d %H:%M')
			kolkata_tz = pytz_timezone('Asia/Kolkata')
			aware_start_time = make_aware(naive_start_time, timezone=kolkata_tz)
			aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

			MembershipBooking.objects.create(
				membership=membership,
				booking_date=booking_date,
				start_time=start_time,
				end_time=aware_end_time,
				slots=s,
				manager=manager,
				court=court,
			)

			court.booked = True
			court.save()

			# book_court_with_thread(court.id, aware_end_time)
			return redirect('/manager/dashboard')
		except (ValueError, Manager.DoesNotExist, Session.DoesNotExist, Membership.DoesNotExist) as e:
			logging.error(e)
			return HttpResponse(str(e), status=400)


def get_membership_details(request):
	barcode = request.GET.get('barcode')
	memberships = Membership.objects.filter(barcode__startswith=barcode)

	data = [
		{
			'barcode': m.barcode,
			'member_name': m.member_name,
			'mobile_number': m.mobile_number,
			'email': m.email,
			'plan': str(m.plan),
			'hours_remaining': m.hours_remaining,
		} for m in memberships
	]

	return JsonResponse(data, safe=False)


# def get_membership_details(request):
#     barcode = request.GET.get('barcode')
#     try:
#         membership = Membership.objects.get(barcode=barcode)
#         data = {
#             'member_name': membership.member_name,
#             'mobile_number': membership.mobile_number,
#             'email': membership.email,
#             'plan': membership.plan,
#             'hours_remaining': membership.hours_remaining,
#         }
#         return JsonResponse(data)
#     except Membership.DoesNotExist:
#         return JsonResponse({'error': 'Membership not found'}, status=404)


class AddAdvancedBookingView(View):
	def get(self, request):
		courts = Court.objects.all()
		slots = slot.objects.all()
		return render(request, 'add_advanced_booking.html', {'courts': courts, 'slots': slots})

	def post(self, request):
		import logging
		logging.basicConfig(level=logging.DEBUG)

		name = request.POST['advanced_normal_name']
		email_id = request.POST['advanced_normal_email']
		mobile_number = request.POST['advanced_normal_mobile_number']
		date = request.POST['advanced_normal_date']
		print("DDDDD ", date)
		start_time = request.POST['advanced_normal_start_tiime']
		end_time = request.POST['advanced_normal_end_time']
		slots = request.POST['advanced_normal_slots']
		print(type(slots))
		print(slots)
		slots = slot.objects.get(id=slots)
		print(slots)
		# payment_method = request.POST['advanced_normal_payment']
		# court_number = request.POST['advanced_normal_court']
		# court = Court.objects.get(court_number=court_number)
		manager_id = request.COOKIES.get('session_id')
		session_data = Session.objects.get(session_key=manager_id).get_decoded()
		manager_id = session_data.get('Manager_Session')
		manager = Manager.objects.get(id=manager_id)
		# discount = request.POST.get('advanced_normal_discount', 0)
		amount = slots.amount
		court = Court.objects.get(court_number=1)

		try:
			naive_start_time = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
			naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
			kolkata_tz = pytz_timezone('Asia/Kolkata')
			aware_start_time = make_aware(naive_start_time, timezone=kolkata_tz)
			aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)
		except ValueError:
			logging.error(ValueError)
			return JsonResponse({'status': 'error', 'message': 'Invalid date/time format.'})

		booking = Booking.objects.create(
			name=name, email=email_id, mobile_number=mobile_number, date=date, start_time=aware_start_time, end_time=aware_end_time, slots=slots, amount=amount, manager=manager, court=court,
			advanced_booked=True)
		# court.booked = False
		# court.save()

		return JsonResponse({'status': 'success', 'booking_id': booking.id})


def test(request):
	return render(request, 'demo.html')


class SlotBookingView(View):
	def get(self, request):
		# booking = get_object_or_404(Booking, id=booking_id)
		return render(request, 'confirm_slot_booking_out.html')

	@csrf_exempt
	def post(self, request):
		booking_id = request.POST['slot_booking_id']
		booking = get_object_or_404(Booking, id=booking_id)
		court = booking.court
		print(request.POST)
		payment_method = request.POST['slot_booking_payment_method']
		print(payment_method)
		booking.payment_method = payment_method
		booking.save()

		court.booked = True
		court.save()
		end_time = booking.end_time

		kolkata_tz = pytz_timezone('Asia/Kolkata')
		date = booking.date
		print(date, end_time)
		naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		book_court_with_thread(court.id, aware_end_time)
		booking.advanced_booked = False
		booking.save()
		return redirect('/manager/dashboard')


def update_status_out(request, booking_id):
	if request.method == 'POST':
		booking = get_object_or_404(MembershipBooking, id=booking_id)
		booking.status_out = False
		booking.save()
		return JsonResponse({'success': True})
	return JsonResponse({'success': False})


class ConfirmAdvancedBookingView(View):
	def get(self, request):
		# booking = get_object_or_404(Booking, id=booking_id)
		return render(request, 'confirm_advanced_booking.html')

	def post(self, request):
		print("Req: ", request.POST)
		booking_id = request.POST['t_search_booking_id']
		booking = get_object_or_404(Booking, id=booking_id)
		print("ID: ", booking)
		court = request.POST['advanced_booking_court']
		c = Court.objects.get(id=court)
		print("Court ", court)
		# print(request.POST)
		# discount = request.POST['advanced_normal_discount']
		# amount = request.POST['advanced_normal_amount']
		# amount = float(amount) - float(discount)
		# booking.amount = int(float(amount))
		# booking.discount = int(float(discount))
		# print("a ", booking.amount)
		booking.court = c
		# payment_method = request.POST['advanced_booking_payment_method']
		# print(payment_method)
		# booking.payment_method = payment_method

		c.booked = True
		c.save()
		end_time = booking.end_time
		# booking.save()

		kolkata_tz = pytz_timezone('Asia/Kolkata')
		date = booking.date
		print(date, end_time)
		naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		# book_court_with_thread(court.id, aware_end_time)
		# booking.is_confirmed = True
		booking.advanced_booked = False
		booking.save()
		return JsonResponse({'success': True, 'booking_id': booking.id}, status=201)


class ConfirmOutSlotBookingView(View):
	def post(self, request):
		booking_id = request.POST['t_outsearch_booking_id']
		print("BID: ", booking_id)
		# booking = get_object_or_404(Booking, id=booking_id)
		booking = Booking.objects.get(id=booking_id)
		print("bOOK: ", booking)
		court = request.POST['out_advanced_booking_court']
		print("Court ", court)
		print(request.POST)
		discount = request.POST['out_advanced_normal_discount']
		amount = request.POST['out_advanced_normal_amount']
		booking.amount = int(float(amount))
		booking.discount = int(float(discount))
		print("a ", booking.amount)

		payment_method = request.POST['out_advanced_booking_payment_method']
		print(payment_method)
		booking.payment_method = payment_method
		c = Court.objects.get(id=court)
		c.unbook()
		c.booked = False
		# booking.save()

		end_time = booking.end_time

		kolkata_tz = pytz_timezone('Asia/Kolkata')
		date = booking.date
		print(date, end_time)
		naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		# book_court_with_thread(court.id, aware_end_time)
		booking.is_confirmed = True
		booking.advanced_booked = False
		booking.save()
		return JsonResponse({'success': True, 'booking_id': booking.id}, status=201)


class M_ConfirmAdvancedBookingView(View):
	def get(self, request):
		# booking = get_object_or_404(Booking, id=booking_id)
		return render(request, 'confirm_advanced_booking.html')

	def post(self, request):
		print(request.POST)
		booking_id = request.POST['m_search_booking_id']
		booking = get_object_or_404(MembershipBooking, id=booking_id)
		court = request.POST['m_advanced_booking_court']
		c = Court.objects.get(court_number=court)
		print("C: ", c)
		booking.court = c
		print(request.POST)
		payment_method = request.POST['m_advanced_booking_payment_method']
		print(payment_method)
		booking.payment_method = payment_method
		booking.save()

		print(court)
		c.booked = True
		c.save()
		end_time = booking.end_time

		kolkata_tz = pytz_timezone('Asia/Kolkata')
		date = booking.booking_date
		print(date, end_time)
		naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		book_court_with_thread(court, aware_end_time)
		booking.advanced_booked = False
		booking.save()
		return redirect('/manager/dashboard')


class M_OutConfirmAdvancedBookingView(View):
	def post(self, request):
		print(request.POST)
		booking_id = request.POST['m_outsearch_booking_id']
		booking_end_time = request.POST['m_outadvanced_booking_end_time']
		booking = get_object_or_404(MembershipBooking, id=booking_id)
		court = request.POST['m_outadvanced_booking_court']
		c = Court.objects.get(court_number=court)
		# c = Court.objects.get(id=court)
		print("C: ", c)
		booking.court = c
		c.unbook()
		c.booked = False
		print(request.POST)
		# payment_method = request.POST['m_advanced_booking_payment_method']
		# print(payment_method)
		# booking.payment_method = payment_method
		# booking.save()

		# print(court)
		# c.booked = True
		# c.save()

		# kolkata_tz = pytz_timezone('Asia/Kolkata')
		# date = booking.booking_date
		# print(date, end_time)
		# naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		# aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		# book_court_with_thread(court, aware_end_time)
		# booking.advanced_booked = False
		booking.is_confirmed = True
		booking.end_time = booking_end_time
		booking.save()
		return JsonResponse({'success': True, 'out_booking_id': booking.id}, status=201)


def search_booking_by_mobile(request):
	mobile_number = request.GET.get('advanced_booking_mobile_number')
	bookings = Booking.objects.filter(mobile_number__startswith=mobile_number, advanced_booked=True)
	print(bookings)

	for booking in bookings:
		data = [
			{
				'id': booking.id,
				'name': booking.name,
				'email': booking.email,
				'mobile_number': booking.mobile_number,
				'booking_date': booking.date,
				'start_time': booking.start_time,
				'end_time': booking.end_time,
				'court': booking.court.court_number,
				'amount': booking.amount,
				'discount': booking.discount,
			}
		]

	return JsonResponse(data, safe=False)


def searchBookingByIDView(request):
	print(request.GET)
	booking_id = request.GET.get('booking_id')  # Use get() to avoid KeyError
	print(booking_id)

	if booking_id is not None:
		booking = get_object_or_404(Booking, id=booking_id)

		data = {
			'id': booking.id,
			'name': booking.name,
			'email': booking.email,
			'mobile_number': booking.mobile_number,
			'booking_date': booking.date,
			'start_time': booking.start_time,
			'end_time': booking.end_time,
			'court': booking.court.court_number,
			'amount': booking.amount,
			'payment_method': booking.payment_method,
			'manager': booking.manager.name if booking.manager else None,  # Handle nullable ForeignKey
			'discount': booking.discount,
			'advanced_booked': booking.advanced_booked,
			'inventory_ball': booking.inventory_ball,
			'inventory_racket': booking.inventory_racket,
		}
		print("AA ", data)
		return JsonResponse(data, safe=False)

	return JsonResponse({'error': 'Invalid booking ID'}, status=400)


# Used for Out button of slot booking
def searchOutBookingByIDView(request):
	print("Req: ", request.GET)
	booking_id = request.GET.get('out_booking_id')  # Use get() to avoid KeyError
	print(booking_id)

	if booking_id is not None:
		booking = get_object_or_404(Booking, id=booking_id)

		data = {
			'id': booking.id,
			'name': booking.name,
			'email': booking.email,
			'mobile_number': booking.mobile_number,
			'booking_date': booking.date,
			'start_time': booking.start_time,
			'end_time': booking.end_time,
			'court': booking.court.court_number,
			'amount': booking.amount,
			'payment_method': booking.payment_method,
			'manager': booking.manager.name if booking.manager else None,  # Handle nullable ForeignKey
			'discount': booking.discount,
			'advanced_booked': booking.advanced_booked,
			'inventory_ball': booking.inventory_ball,
			'inventory_racket': booking.inventory_racket,
		}
		print("BBB ", data)
		return JsonResponse(data, safe=False)

	return JsonResponse({'error': 'Invalid booking ID'}, status=400)


class M_SearchBookingByIDView(View):
	def get(self, request):
		print(request.GET)
		booking_id = request.GET.get('m_booking_id')
		print(booking_id)
		booking = MembershipBooking.objects.get(id=booking_id, advanced_booked=True)
		# print(booking)

		data = {
			'id': booking.id,
			'name': booking.membership.member_name,
			'email': booking.membership.email,
			'mobile_number': booking.membership.mobile_number,
			'booking_date': booking.created_at.strftime('%d/%m/%y'),
			'start_time': booking.start_time,
			'end_time': booking.end_time,
			# 'court': booking.court.court_number,
		}

		return JsonResponse(data, safe=False)


class M_OutSearchBookingByIDView(View):
	def get(self, request):
		print(request.GET)
		booking_id = request.GET.get('m_outbooking_id')
		print(booking_id)
		booking = MembershipBooking.objects.get(id=booking_id)
		# print(booking)

		data = {
			'id': booking.id,
			'name': booking.membership.member_name,
			'email': booking.membership.email,
			'mobile_number': booking.membership.mobile_number,
			'booking_date': booking.created_at.strftime('%d/%m/%y'),
			'start_time': booking.start_time,
			'end_time': booking.end_time,
			'court': booking.court.court_number,
		}

		return JsonResponse(data, safe=False)


def get_booking_details(request):
	booking_id = request.GET.get('booking_id')
	try:
		booking = Booking.objects.get(id=booking_id, advanced_booked=True)
		print(booking)
		data = {
			'name': booking.name,
			'email': booking.email,
			'mobile_number': booking.mobile_number,
			'booking_date': booking.date,
			'start_time': booking.start_time,
			'end_time': booking.end_time,
		}
		return JsonResponse(data)
	except Booking.DoesNotExist:
		return JsonResponse({}, status=404)


class AddMembershipAdvancedBookingView(View):
	import logging
	logging.basicConfig(level=logging.DEBUG)

	def get(self, request):
		courts = Court.objects.all()
		slots = slot.objects.all()
		return render(request, 'add_membership_advanced_booking.html', {'courts': courts, 'slots': slots})

	def post(self, request):

		membership_id = request.POST['membership_id']
		membership = get_object_or_404(Membership, id=membership_id)
		date = request.POST['membership_advanced_date']
		start_time = request.POST['membershipbooking_start_time']
		end_time = request.POST['membershipbooking_end_time']
		s = request.POST['membershipbooking_slots']
		print("ff", s)
		slots = slot.objects.get(id=s)
		print("ssssssss ", slots)
		# payment_method = request.POST['payment_method']
		# court_number = request.POST['court']
		# court = Court.objects.get(court_number=court_number)
		manager_id = request.COOKIES.get('session_id')
		session_data = Session.objects.get(session_key=manager_id).get_decoded()
		manager_id = session_data.get('Manager_Session')
		manager = Manager.objects.get(id=manager_id)
		# discount = request.POST.get('discount', 0)
		# amount = slots.amount

		try:
			naive_start_time = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
			naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')
			kolkata_tz = pytz_timezone('Asia/Kolkata')
			aware_start_time = make_aware(naive_start_time, timezone=kolkata_tz)
			aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)
		except ValueError:
			logging.error('Invalid date/time format.')
			return JsonResponse({'status': 'error', 'message': 'Invalid date/time format.'})

		booking = MembershipBooking.objects.create(
			membership=membership, booking_date=date, start_time=aware_start_time, end_time=aware_end_time,
			slots=slots, manager=manager, advanced_booked=True
		)
		# court.booked = False
		# court.save()

		return redirect('/manager/dashboard')


class ConfirmAdvancedMembershipBookingView(View):
	def get(self, request, booking_id):
		booking = get_object_or_404(MembershipBooking, id=booking_id)
		return render(request, 'confirm_advanced_membership_booking.html', {'booking': booking})

	def post(self, request, booking_id):
		booking = get_object_or_404(MembershipBooking, id=booking_id)
		court = booking.court
		payment_method = request.POST['payment_method']
		inventory_ball = Inventory.objects.get(id=1)
		inventory_racket = Inventory.objects.get(id=2)

		booking.membership.hours_remaining -= booking.slots
		booking.payment_method = payment_method
		booking.save()

		court.booked = True
		court.save()
		end_time = booking.end_time

		kolkata_tz = pytz_timezone('Asia/Kolkata')
		date = booking.booking_date
		naive_end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M:%S')
		aware_end_time = make_aware(naive_end_time, timezone=kolkata_tz)

		book_court_with_thread(court.id, aware_end_time)
		return redirect('/manager/dashboard')


from django.http import JsonResponse
from .models import Membership


# class SearchMembershipView(View):
#     def get(self, request):
#         number = request.GET.get('mobile_number')
#         try:
#             membership = Membership.objects.get(mobile_number=number)
#             return JsonResponse({
#                 'status': 'success',
#                 'membership': {
#                     'id': membership.id,
#                     'name': membership.member_name,
#                     'email': membership.email,
#                     'mobile_number': membership.mobile_number
#                 }
#             })
#         except Membership.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Membership not found.'})

class SearchMembershipView(View):
	def get(self, request):
		mobile_number = request.GET.get('mobile_number', '')
		memberships = Membership.objects.filter(mobile_number__startswith=mobile_number)[:10]  # Limit results for performance
		membership_list = [
			{
				'id': membership.id,
				'name': membership.member_name,
				'email': membership.email,
				'mobile_number': membership.mobile_number
			}
			for membership in memberships
		]
		return JsonResponse({'status': 'success', 'memberships': membership_list})


class CheckBarcodeView(View):
	def get(self, request):
		barcode = request.GET.get('barcode', '')
		members = Membership.objects.filter(barcode__startswith=barcode)
		members_list = list(members.values('id', 'member_name', 'mobile_number', 'email'))
		return JsonResponse(members_list, safe=False)


class GetMemberDataView(View):
	def get(self, request, member_id):
		member = get_object_or_404(Membership, id=member_id)
		member_data = {
			'member_name': member.member_name,
			'mobile_number': member.mobile_number,
			'email': member.email,
			'plan': member.plan.id,
			'expiration_date': member.expiration_date.strftime('%m/%d/%Y'),
			'payment_method': member.payment_method,
			'status': member.status,
		}
		return JsonResponse(member_data)


class SearchMembershipByBarcodeView(View):
	def get(self, request):
		barcode = request.GET.get('barcode', '')
		memberships = Membership.objects.filter(barcode__startswith=barcode)
		result = [{'barcode': m.barcode, 'member_name': m.member_name, 'mobile_number': m.mobile_number} for m in memberships]
		return JsonResponse(result, safe=False)


class GetMembershipView(View):
	def get(self, request, barcode):
		membership = get_object_or_404(Membership, barcode=barcode)
		result = {
			'barcode': membership.barcode,
			'member_name': membership.member_name,
			'mobile_number': membership.mobile_number,
			'email': membership.email,
			'expiration_date': membership.expiration_date.strftime('%m/%d/%Y'),
			'payment_method': membership.payment_method,
			'status': membership.status,
			'hours_remaining': membership.hours_remaining
		}
		return JsonResponse(result)


class PrintReceiptView(View):
	def get(self, request, booking_id):
		booking = get_object_or_404(Booking, id=booking_id)
		return render(request, 'print_receipt.html', {'booking': booking})

	def post(self, request, booking_id):
		booking = get_object_or_404(Booking, id=booking_id)
		template_path = 'receipt_template.html'
		context = {'booking': booking}
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="receipt_{booking.id}.pdf"'
		template = get_template(template_path)
		html = template.render(context)
		pisa_status = pisa.CreatePDF(html, dest=response)
		if pisa_status.err:
			return HttpResponse('We had some errors with generating the PDF')
		return response


class ManageMembershipsView(View):
	def get(self, request):
		memberships = Membership.objects.all()
		return render(request, 'manage_memberships.html', {'memberships': memberships})


class ManageManagersView(View):
	def get(self, request):
		managers = Manager.objects.all()
		return render(request, 'manage_managers.html', {'managers': managers})


class ViewCustomersView(View):
	def get(self, request):
		customers = Customer.objects.all()
		return render(request, 'view_customers.html', {'customers': customers})


from .models import Inventory


class InventoryListView(View):
	def get(self, request):
		inventory_items = Inventory.objects.all()
		return render(request, 'inventory_list.html', {'inventory_items': inventory_items})


class AddInventoryView(View):
	def get(self, request):
		return render(request, 'add_inventory.html')

	def post(self, request):
		item_name = request.POST['item_name']
		quantity = request.POST['quantity']
		manager = request.COOKIES.get('session_id')
		# session_data = Session.objects.get(session_key=manager).get_decoded()
		# manager_id = session_data.get('Manager_Session')
		# manager = Manager.objects.get(id=manager_id)
		Inventory.objects.create(item_name=item_name, quantity=quantity, updated_at=now())
		return redirect('/manager/inventory/')


class UpdateInventoryView(View):
	def get(self, request, item_id):
		inventory_item = get_object_or_404(Inventory, id=item_id)
		return render(request, 'update_inventory.html', {'inventory_item': inventory_item})

	def post(self, request, item_id):
		inventory_item = get_object_or_404(Inventory, id=item_id)
		inventory_item.item_name = request.POST['item_name']
		inventory_item.quantity = request.POST['quantity']
		inventory_item.save()
		return redirect('/inventory/')


class DeleteInventoryView(View):
	def get(self, request, item_id):
		inventory_item = get_object_or_404(Inventory, id=item_id)
		inventory_item.delete()
		return redirect('/inventory/')
