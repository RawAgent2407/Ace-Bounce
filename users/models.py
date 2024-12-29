from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.utils.timezone import now
from datetime import datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class SuperAdminManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class SuperAdmin(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)  # Make username optional
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = SuperAdminManager()

    def __str__(self):
        return self.email


class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Manager(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    @property
    def total_booking(self):
        return self.booking_set.count()

    @property
    def collection(self):
        return self.booking_set.aggregate(total=Sum('amount'))['total'] or 0

    def __str__(self):
        return self.email


class Court(models.Model):
    court_number = models.IntegerField(unique=True, default=1)
    booked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Add any custom behavior before saving the court instance
        print(f'Saving Court {self.court_number} with booked status {self.booked}')

        # Call the original save method to save the instance
        super().save(*args, **kwargs)

        # Add any custom behavior after saving the court instance
        print(f'Court {self.court_number} saved successfully')

    def book(self):
        """Mark the court as booked."""
        self.booked = True
        self.save()

    def unbook(self):
        """Mark the court as unbooked."""
        self.booked = False
        self.save()


    def __str__(self):
        return f'Court {self.court_number} booked: {self.booked}'


class Amount(models.Model):
    amount = models.IntegerField(default=700)
    updated_at = models.DateTimeField(auto_now=True)


class slot(models.Model):
    number = models.IntegerField()
    amount = models.IntegerField(default=700)
    hours = models.IntegerField(default=1)

    def __str__(self):
        return f'Slot {self.number}'


class Booking(models.Model):
    # b_id = models.IntegerField(auto_created=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField(default=now().time())
    end_time = models.TimeField(default=now().time())
    slots = models.ForeignKey(slot, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.IntegerField(default=700)
    court = models.ForeignKey(Court, null=True, blank=True, on_delete=models.SET_NULL)
    payment_method = models.CharField(max_length=10, choices=[('Cash', 'Cash'), ('UPI', 'UPI')], default='Cash')
    manager = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0)
    advanced_booked = models.BooleanField(default=False)
    inventory_ball = models.IntegerField(default=1)
    inventory_racket = models.IntegerField(default=2)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"

    #
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # self.court.booked = True
        # self.court.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if not self.court.bookings.filter(end_time__gt=datetime.now()).exists():
            self.court.booked = False
            self.court.save()

    @classmethod
    def get_all_bookings(cls):
        return cls.objects.all()


class Membership_Plan(models.Model):
    name = models.CharField(max_length=100)
    amount = models.IntegerField()
    Total_hours = models.IntegerField()
    validity_days = models.IntegerField(default=7)
    discount_percentage = models.FloatField(default=0)

    def __str__(self):
        return self.name


from django.db import models
from django.utils.timezone import now


class Membership(models.Model):
    barcode = models.CharField(max_length=100, unique=True, default='20240810000', null=True, blank=True)
    member_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    hours_remaining = models.IntegerField(default=0)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, null=True, blank=True)
    expiration_date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=[('Cash', 'Cash'), ('UPI', 'UPI')], default='Cash')
    created_at = models.CharField(max_length=50, default=now().date())
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    plan = models.ForeignKey('Membership_Plan', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.member_name} - {self.mobile_number}'



class MembershipBooking(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField(default=now().time())
    end_time = models.TimeField(default=now().time())
    slots = models.ForeignKey('slot', on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=0)
    advanced_booked = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=10, choices=[('Cash', 'Cash'), ('UPI', 'UPI')], default='Cash')
    is_confirmed = models.BooleanField(default=False)
    status_out = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.membership.member_name} - {self.booking_date} - {self.start_time}'


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    booking_history = models.TextField()

    def __str__(self):
        return self.email


from django.db import models
from django.utils.timezone import now


class Inventory(models.Model):
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    # manager = models.ForeignKey('Manager', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
