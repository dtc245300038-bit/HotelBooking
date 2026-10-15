
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Room, Customer, Booking


# Định dạng giá tiền Việt Nam: 500000 -> 500.000
def format_vnd(amount):
    return f"{amount:,.0f}".replace(",", ".")


def home(request):
    rooms = Room.objects.filter(is_available=True)

    for room in rooms:
        room.price_vnd = format_vnd(room.price_per_night)

    return render(
        request,
        'booking/home.html',
        {'rooms': rooms}
    )


def room_list(request):
    rooms = Room.objects.all()

    for room in rooms:
        room.price_vnd = format_vnd(room.price_per_night)

    return render(
        request,
        'booking/room_list.html',
        {'rooms': rooms}
    )


def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        check_in_raw = request.POST.get('check_in', '').strip()
        check_out_raw = request.POST.get('check_out', '').strip()
        notes = request.POST.get('notes', '').strip()

        # 1. Kiểm tra thông tin bắt buộc
        if not full_name or not email or not phone:
            messages.error(
                request,
                'Vui lòng nhập đầy đủ họ tên, email và số điện thoại.'
            )
            return render(
                request,
                'booking/book_room.html',
                {'room': room}
            )

        # 2. Kiểm tra định dạng ngày
        try:
            check_in = date.fromisoformat(check_in_raw)
            check_out = date.fromisoformat(check_out_raw)
        except (ValueError, TypeError):
            messages.error(
                request,
                'Ngày nhận phòng hoặc ngày trả phòng không hợp lệ.'
            )
            return render(
                request,
                'booking/book_room.html',
                {'room': room}
            )

        # 3. Kiểm tra ngày trả phòng
        if check_out <= check_in:
            messages.error(
                request,
                'Ngày trả phòng phải sau ngày nhận phòng.'
            )
            return render(
                request,
                'booking/book_room.html',
                {'room': room}
            )

        # 4. Không cho phép đặt phòng trong quá khứ
        if check_in < date.today():
            messages.error(
                request,
                'Ngày nhận phòng không được ở trong quá khứ.'
            )
            return render(
                request,
                'booking/book_room.html',
                {'room': room}
            )

        # 5. Kiểm tra phòng có bị trùng lịch đặt hay không
        overlapping_booking = Booking.objects.filter(
            room=room,
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=['pending', 'confirmed', 'checked_in'],
        ).exists()

        if overlapping_booking:
            messages.error(
                request,
                'Phòng này đã có người đặt trong khoảng thời gian '
                'bạn chọn. Vui lòng chọn ngày khác.'
            )
            return render(
                request,
                'booking/book_room.html',
                {'room': room}
            )

        # 6. Tạo hoặc lấy khách hàng theo email
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'phone': phone,
            }
        )

        # 7. Tạo đơn đặt phòng
        booking = Booking.objects.create(
            customer=customer,
            room=room,
            check_in=check_in,
            check_out=check_out,
            notes=notes,
            status='pending',
        )

        # 8. Chuyển đến trang xác nhận đặt phòng
        return redirect(
            'booking_success',
            booking_id=booking.id
        )

    return render(
        request,
        'booking/book_room.html',
        {'room': room}
    )


def booking_success(request, booking_id):
    # Lấy thông tin đơn đặt phòng
    booking = get_object_or_404(
        Booking.objects.select_related('customer', 'room'),
        id=booking_id
    )

    # Tính số đêm lưu trú
    nights = (booking.check_out - booking.check_in).days

    # Hiển thị trang xác nhận
    return render(
        request,
        'booking/booking_success.html',
        {
            'booking': booking,
            'nights': nights,
        }
    )