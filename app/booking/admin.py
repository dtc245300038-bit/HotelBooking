
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect

from .models import Room, Customer, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number',
        'room_type',
        'price_per_night',
        'capacity',
        'is_available',
    )
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'phone',
        'created_at',
    )
    search_fields = ('full_name', 'email', 'phone')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'room',
        'check_in',
        'check_out',
        'status',
        'total_price',
        'booking_actions',
    )

    list_filter = ('status', 'check_in')
    search_fields = (
        'customer__full_name',
        'room__room_number',
    )
    date_hierarchy = 'check_in'

    readonly_fields = ('total_price',)

    fields = (
        'customer',
        'room',
        'check_in',
        'check_out',
        'status',
        'total_price',
        'notes',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:booking_id>/confirm/',
                self.admin_site.admin_view(self.confirm_booking),
                name='booking-confirm',
            ),
            path(
                '<int:booking_id>/cancel/',
                self.admin_site.admin_view(self.cancel_booking),
                name='booking-cancel',
            ),
            path(
                '<int:booking_id>/check-in/',
                self.admin_site.admin_view(self.check_in_booking),
                name='booking-check-in',
            ),
            path(
                '<int:booking_id>/check-out/',
                self.admin_site.admin_view(self.check_out_booking),
                name='booking-check-out',
            ),
        ]
        return custom_urls + urls

    @admin.display(description='Thao tác')
    def booking_actions(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Xác nhận</a> '
                '<a class="button" href="{}">Hủy đặt phòng</a>',
                f'{obj.pk}/confirm/',
                f'{obj.pk}/cancel/',
            )

        if obj.status == 'confirmed':
            return format_html(
                '<a class="button" href="{}">Nhận phòng</a> '
                '<a class="button" href="{}">Hủy đặt phòng</a>',
                f'{obj.pk}/check-in/',
                f'{obj.pk}/cancel/',
            )

        if obj.status == 'checked_in':
            return format_html(
                '<a class="button" href="{}">Trả phòng</a>',
                f'{obj.pk}/check-out/',
            )

        return 'Không có thao tác'

    def confirm_booking(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)

        if booking.status != 'pending':
            self.message_user(
                request,
                'Chỉ xác nhận được đơn đang chờ xác nhận.',
                level=messages.WARNING,
            )
        else:
            booking.status = 'confirmed'
            booking.save()
            self.message_user(
                request,
                'Đã xác nhận đặt phòng.',
                level=messages.SUCCESS,
            )

        return redirect('../')

    def cancel_booking(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)

        if booking.status not in ('pending', 'confirmed'):
            self.message_user(
                request,
                'Chỉ hủy được đơn đang chờ xác nhận hoặc đã xác nhận.',
                level=messages.WARNING,
            )
        else:
            booking.status = 'cancelled'
            booking.save()
            self.message_user(
                request,
                'Đã hủy đặt phòng.',
                level=messages.SUCCESS,
            )

        return redirect('../')

    def check_in_booking(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)

        if booking.status != 'confirmed':
            self.message_user(
                request,
                'Chỉ nhận phòng khi đơn đã được xác nhận.',
                level=messages.WARNING,
            )
        else:
            booking.status = 'checked_in'
            booking.save()
            self.message_user(
                request,
                'Khách đã nhận phòng.',
                level=messages.SUCCESS,
            )

        return redirect('../')

    def check_out_booking(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)

        if booking.status != 'checked_in':
            self.message_user(
                request,
                'Chỉ trả phòng khi khách đã nhận phòng.',
                level=messages.WARNING,
            )
        else:
            booking.status = 'checked_out'
            booking.save()
            self.message_user(
                request,
                'Khách đã trả phòng.',
                level=messages.SUCCESS,
            )

        return redirect('../')