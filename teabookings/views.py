from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now

import stripe
from django.conf import settings
from .models import User, TeaLesson, Cart, CartItem
stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    return render(request, "teabookings/index.html")


def tealessons(request):
    tea = TeaLesson.objects.all()
    return render(request,"teabookings/tealesson.html",{
        "tea" : tea
    })


def extradetails(request,id):
    lesson = get_object_or_404(TeaLesson, id=id)
    return render(request, 'teabookings/detail.html', {'lesson': lesson})


def add_to_cart(request, lesson_id):
    if request.method == "POST":
        lesson = get_object_or_404(TeaLesson, id=lesson_id)
        user = request.user

        if not user.is_authenticated:
            return redirect('login')  # Redirect to login if the user is not authenticated

        # Get or create cart for the logged-in user
        cart, _ = Cart.objects.get_or_create(user=user)

        # Add or update the item in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, tea_lesson=lesson)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        # Redirect back to the detail page
        return redirect('extradetails', id=lesson_id)

    return redirect('index')


def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
        return JsonResponse({"cart_count": count})
    return JsonResponse({"cart_count": 0})



def displaycart(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    # Get the cart for the logged-in user
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []  # Use empty list if no cart exists

    # Add subtotals to each item and calculate total price
    cart_details = []
    total_price = 0
    for item in cart_items:
        subtotal = item.quantity * item.tea_lesson.price
        total_price += subtotal
        cart_details.append({
            'id': item.id,
            'name': item.tea_lesson.name,
            'imgUrl': item.tea_lesson.imgUrl,
            'price': item.tea_lesson.price,
            'quantity': item.quantity,
            'subtotal': subtotal,
            'selected_date': item.selected_date  # Include the selected date
        })

    if request.method == "POST":
        # Process selected dates and times
        for item in cart_items:
            date_str = request.POST.get(f"date_{item.id}")
            time_str = request.POST.get(f"time_{item.id}")
            if date_str and time_str:
                # Combine date and time into a single datetime
                selected_datetime = f"{date_str} {time_str}"
                item.selected_date = selected_datetime
                item.save()

        # Redirect to Stripe checkout (implementation for Stripe to follow)
        return redirect("stripe_checkout")

    return render(request, 'teabookings/cart.html', {
        'cart_details': cart_details,
        'total_price': total_price,
        'today': now().date(),  # Pass today's date for validation in the template
         'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('login')

    # Retrieve the cart item
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Delete the cart item
    cart_item.delete()

    # Redirect back to the cart page
    return redirect('displaycart')


def stripe_checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    # Get the cart for the logged-in user
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Prepare Stripe line items
    line_items = []
    for item in cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.tea_lesson.name,
                },
                'unit_amount': int(item.tea_lesson.price * 100),  # Convert to cents
            },
            'quantity': item.quantity,
        })

    # Create Stripe Checkout Session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/displaycart'),
        )

         # Clear the cart after session creation but before redirect
        return JsonResponse({'url': session.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart.items.all().delete()
    cart.save()
    return render(request, 'teabookings/success.html')



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "teabookings/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "teabookings/login.html")


def displaybookings(request):
    if not request.user.is_authenticated:
        return redirect('login')

    current_bookings = CartItem.objects.filter(
        cart__user=request.user, is_booked=True, selected_date__gte=now()
    )
    past_bookings = CartItem.objects.filter(
        cart__user=request.user, is_booked=True, selected_date__lt=now()
    )

    return render(request, 'teabookings/bookings.html', {
        'current_bookings': current_bookings,
        'past_bookings': past_bookings,
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "teabookings/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "teabookings/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "teabookings/register.html")
