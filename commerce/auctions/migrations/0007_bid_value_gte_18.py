# Generated by Django 3.2.6 on 2021-09-05 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_bid'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='bid',
            constraint=models.CheckConstraint(check=models.Q(('value__gte', 18)), name='value_gte_18'),
        ),
    ]
