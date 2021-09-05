# Generated by Django 3.2.6 on 2021-09-05 05:45

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_bid_value_gte_18'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bid',
            name='value_gte_18',
        ),
        migrations.AddField(
            model_name='bid',
            name='starting_bid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddConstraint(
            model_name='bid',
            constraint=models.CheckConstraint(check=models.Q(('value__gte', django.db.models.expressions.F('starting_bid'))), name='value_gte_starting_bid'),
        ),
    ]
