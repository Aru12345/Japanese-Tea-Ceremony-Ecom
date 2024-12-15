from .models import Cart 

# Calculates the number of items in a users cart
# If there are not items in cart or user isnt authenticated it returns 0
def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {'cart_count': cart.items.count() if cart else 0} 
    return {'cart_count': 0}
    
