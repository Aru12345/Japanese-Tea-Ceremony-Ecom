from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tealessons", views.tealessons, name="tealessons"),
    path("tealessons/<int:id>", views.extradetails, name="extradetails"),
    path("add-to-cart/<int:lesson_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart-count/", views.cart_count, name="cart_count"),
    path("displaycart",views.displaycart,name="displaycart"),
    path("remove-from-cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path('checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path("bookings/", views.displaybookings, name="displaybookings"),
    path('search/', views.search_tealessons, name='search_tealessons'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
