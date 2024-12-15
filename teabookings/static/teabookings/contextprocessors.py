from .models import Cart # type: ignore

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {'cart_count': cart.items.count() if cart else 0}
    return {'cart_count': 0}
