# Generated by Django 3.2.6 on 2021-09-09 08:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_listing_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]