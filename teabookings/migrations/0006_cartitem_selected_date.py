# Generated by Django 5.1.1 on 2024-12-07 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teabookings', '0005_cart_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='selected_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]