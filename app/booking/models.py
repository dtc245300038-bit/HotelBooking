from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Phòng đơn'),
        ('double', 'Phòng đôi'),
        ('suite', 'Suite'),
        ('family', 'Phòng gia đình'),
    ]

    room_number = models.CharField(max_length=10, unique=True, verbose_name="Số phòng")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name="Loại phòng")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Giá mỗi đêm")
    capacity = models.PositiveIntegerField(default=2, verbose_name="Sức chứa")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_available = models.BooleanField(default=True, verbose_name="Còn trống")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phòng"
        verbose_name_plural = "Danh sách phòng"
        ordering = ['room_number']

    def __str__(self):
        return f"Phòng {self.room_number} - {self.get_room_type_display()}"


class Customer(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    id_card = models.CharField(max_length=20, blank=True, verbose_name="CMND/CCCD")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Danh sách khách hàng"
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('checked_in', 'Đã nhận phòng'),
        ('checked_out', 'Đã trả phòng'),
        ('cancelled', 'Đã hủy'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings', verbose_name="Khách hàng")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name="Phòng")
    check_in = models.DateField(verbose_name="Ngày nhận phòng")
    check_out = models.DateField(verbose_name="Ngày trả phòng")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True, verbose_name="Tổng tiền")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đặt phòng"
        verbose_name_plural = "Danh sách đặt phòng"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.full_name} - Phòng {self.room.room_number}"

    def save(self, *args, **kwargs):
        # Tự động tính tổng tiền
        if self.check_in and self.check_out and self.room:
            nights = (self.check_out - self.check_in).days
            if nights > 0:
                self.total_price = nights * self.room.price_per_night
        super().save(*args, **kwargs)