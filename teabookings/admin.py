from django.contrib import admin
from .models import TeaLesson
from .models import User
from .models import CartItem
from .models import Booking
from .models import BookingItem
from .models import Filter

admin.site.register(User)
admin.site.register(TeaLesson)
admin.site.register(CartItem)
admin.site.register(Booking)
admin.site.register(BookingItem)
admin.site.register(Filter)