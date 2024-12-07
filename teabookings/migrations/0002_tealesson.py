# Generated by Django 5.1.1 on 2024-12-06 18:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teabookings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeaLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('history', models.CharField(max_length=600)),
                ('price', models.IntegerField()),
                ('itemsNeeded', models.CharField(max_length=100)),
                ('time', models.IntegerField()),
                ('difficulty', models.CharField(max_length=15)),
                ('imgUrl', models.CharField(max_length=500)),
                ('favorite', models.ManyToManyField(blank=True, null=True, related_name='favoritelist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]