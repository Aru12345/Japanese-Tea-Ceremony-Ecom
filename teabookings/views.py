from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Q
from django.contrib import messages
from datetime import datetime

import stripe
from django.conf import settings
from .models import User, TeaLesson, Cart, CartItem,Booking,BookingItem, Filter

stripe.api_key = settings.STRIPE_SECRET_KEY

# Home page view
def index(request):
    return render(request, "teabookings/index.html")


# Displays all tea lessons 
def tealessons(request):
    tea = TeaLesson.objects.all()
    filterList = Filter.objects.all()
    return render(request,"teabookings/tealesson.html",{
        "tea" : tea,
        "filter":filterList
    })

# Lessons are filtered and displayed using user input
def displayFilter(request):
    if request.method == "POST":
        filterSelected = request.POST['filter']
        if filterSelected == "all":
            currentLessons = TeaLesson.objects.all()  # all lessons
        else:
            try:
                selectedFilter = Filter.objects.get(filterName=filterSelected)
                currentLessons = TeaLesson.objects.filter(filter=selectedFilter)
            except Filter.DoesNotExist:
                currentLessons = TeaLesson.objects.none()
        
        filterList = Filter.objects.all()
        return render(request, "teabookings/tealesson.html", {
            "tea": currentLessons, 
            "filter": filterList  
        })


# View more details about tea lessons
def extradetails(request,id):
    lesson = get_object_or_404(TeaLesson, id=id)
    favInfo = request.user in lesson.favorite.all()
    return render(request, 'teabookings/detail.html', {
        'lesson': lesson,
        'favInfo': favInfo                                              
})


# Removes a lesson from a users favorite list
def removeFavList(request, id):
    teaInfo = TeaLesson.objects.get(pk=id)
    currentUser = request.user
    teaInfo.favorite.remove(currentUser)
    return HttpResponseRedirect(reverse("extradetails", args=(id, )))


# Adds an item to a users favlist
def addFavList(request, id):
    teaInfo = TeaLesson.objects.get(pk=id)
    currentUser = request.user
    teaInfo.favorite.add(currentUser)
    return HttpResponseRedirect(reverse("extradetails", args=(id, )))


# Displays all the listings in a users favorite list
def displayFavorite(request):
    currentUser = request.user
    currentFavs = currentUser.favoritelist.all()
    return render(request, "teabookings/favorites.html", {
        "favorites": currentFavs
    })


# Adds a tea lessons to users cart or updates the quantity of item in cart
def add_to_cart(request, lesson_id):
    if request.method == "POST":
        lesson = get_object_or_404(TeaLesson, id=lesson_id)
        user = request.user

        if not user.is_authenticated:
            return redirect('login')  

        # Get or create carte
        cart, _ = Cart.objects.get_or_create(user=user)

        # Add or update the item in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, tea_lesson=lesson)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        # Redirect back to the detail page
        return redirect('extradetails', id=lesson_id)
    return redirect('index')


# Returns the current cart count as JSON response
def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
        return JsonResponse({"cart_count": count})
    return JsonResponse({"cart_count": 0})


# Displays all the contents of cart
def displaycart(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    # Get the cart for the logged in user
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []  # Use empty list if no cart exists

    # Adding subtotals to each item to calculate total price
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
            'selected_date': item.selected_date  
        })

    if request.method == "POST":
        # Processing selected dates and times
        for item in cart_items:
            date_str = request.POST.get(f"date_{item.id}")
            time_str = request.POST.get(f"time_{item.id}")
            if date_str and time_str:
                # Combine date and time into a single datetime
                selected_datetime = f"{date_str} {time_str}"
                item.selected_date = selected_datetime
                item.save()

        # Redirecting to Stripe checkout
        return redirect("stripe_checkout")

    return render(request, 'teabookings/cart.html', {
        'cart_details': cart_details,
        'total_price': total_price,
        'today': now().date(),  # Todays date to check for validations
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


# Removes an item from cart
def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user) # Retrieving the cart item
    cart_item.delete()
    return redirect('displaycart')


# Handles payment checkout with Stripe and 
def stripe_checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Validate and save selected dates
    for item in cart.items.all():
        date_str = request.POST.get(f"date_{item.id}")
        time_str = request.POST.get(f"time_{item.id}")
        if date_str and time_str:
            try:
                selected_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                item.selected_date = selected_datetime
                item.save()
            except ValueError:
                return JsonResponse({'error': f"Invalid date or time for {item.tea_lesson.name}"}, status=400)
        else:
            return JsonResponse({'error': f"Date and time are required for {item.tea_lesson.name}"}, status=400)

    line_items = []
    total_price = 0
    for item in cart.items.all():
        total_price += item.quantity * item.tea_lesson.price
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

    try:
        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/displaycart'),
        )
        return JsonResponse({'url': session.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Handles successful booking creation and payment
def payment_success(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('displaycart')

    # Create a Booking
    total_price = sum(item.quantity * item.tea_lesson.price for item in cart.items.all())
    booking = Booking.objects.create(user=request.user, total_price=total_price)

    # Create BookingItems
    for item in cart.items.all():
        BookingItem.objects.create(
            booking=booking,
            tea_lesson=item.tea_lesson,
            quantity=item.quantity,
            selected_date=item.selected_date,
            price=item.tea_lesson.price
        )

    # Clear the cart
    cart.items.all().delete()

    messages.success(request, "Your booking was successful!")
    return render(request, 'teabookings/success.html', {'booking': booking})


# Displays all current and past booking.
def displaybookings(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Current bookings
    current_booking_items = BookingItem.objects.filter(
        booking__user=request.user, 
        selected_date__gte=now()
    ).order_by('selected_date')

    # Past bookings
    past_booking_items = BookingItem.objects.filter(
        booking__user=request.user, 
        selected_date__lt=now()
    ).order_by('-selected_date')

    return render(request, 'teabookings/bookings.html', {
        'current_booking_items': current_booking_items,
        'past_booking_items': past_booking_items,
    })


# Searches tea lessons by name
def search_tealessons(request):
    if request.method == "POST":
        query = request.POST.get('search_query', '')
    else:
        query = request.GET.get('search_query', '')

    results = TeaLesson.objects.filter(Q(name__icontains=query)) if query else TeaLesson.objects.all()
    return render(request, 'teabookings/search_results.html', {'tea': results})


# Logs a user in the application
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


# Logs a user out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# Registers a new user
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