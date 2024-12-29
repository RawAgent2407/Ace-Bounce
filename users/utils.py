import threading
from django.http import JsonResponse
from django.utils import timezone
from .models import Court, Inventory
import pytz

def update_court_status(court_id, end_time):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
    print(f'Court ID: {court_id}, End Time: {end_time}')
    
    # Ensure end_time is timezone-aware
    if end_time.tzinfo is None:
        end_time = kolkata_tz.localize(end_time)
    
    print(f'End Time: {end_time}')
    
    # Get the current time in Asia/Kolkata timezone
    now = timezone.now().astimezone(kolkata_tz)
    print(f'Current Time: {now}')
    
    sleep_time = (end_time - now).total_seconds()
    print(f'Sleeping for {sleep_time} seconds')
    
    if sleep_time > 0:
        threading.Event().wait(sleep_time)

    court = Court.objects.get(id=court_id)
    court.booked = False
    court.save()

    # Replenish inventory
    racket = Inventory.objects.get(id=1)
    ball = Inventory.objects.get(id=2)
    racket.quantity += 2
    ball.quantity += 2
    racket.save()
    ball.save()

def book_court_with_thread(court_id, end_time):
    court = Court.objects.get(id=court_id)
    court.booked = True
    court.save()
    # racket = Inventory.objects.get(id=1)
    # ball = Inventory.objects.get(id=2)
    racket = Inventory.objects.get(item_name__iexact='racket')
    ball = Inventory.objects.get(item_name__iexact='ball')
    if racket.quantity >= 2 and ball.quantity >= 2:
        racket.quantity -= 2
        ball.quantity -= 2
        racket.save()
        ball.save()
    else:
        return JsonResponse({'status': 'error', 'message': 'Inventory not available'})
    thread = threading.Thread(target=update_court_status, args=(court_id, end_time))
    thread.start()
