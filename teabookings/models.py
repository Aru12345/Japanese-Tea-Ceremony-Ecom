from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class TeaLesson(models.Model):
    name = models.CharField(max_length=35)
    history = models.CharField(max_length=1000)
    price = models.IntegerField()
    itemsNeeded = models.CharField(max_length=1000)
    time = models.IntegerField()
    difficulty = models.CharField(max_length=15)
    imgUrl = models.CharField(max_length=500)
    favorite = models.ManyToManyField(User, blank=True, null=True, related_name="favoritelist")

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    tea_lesson = models.ForeignKey(TeaLesson, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    selected_date = models.DateTimeField(null=True, blank=True)
    is_booked = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.quantity} x {self.tea_lesson.name}"