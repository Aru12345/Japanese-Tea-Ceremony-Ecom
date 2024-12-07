from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import User, TeaLesson, Cart, CartItem


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
        return JsonResponse({"cart_count": count})  # Return valid JSON
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
            'name': item.tea_lesson.name,
            'imgUrl': item.tea_lesson.imgUrl,
            'price': item.tea_lesson.price,
            'quantity': item.quantity,
            'subtotal': subtotal
        })

    return render(request, 'teabookings/cart.html', {
        'cart_details': cart_details,
        'total_price': total_price
    })
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
