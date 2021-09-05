# Generated by Django 3.2.6 on 2021-09-05 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listing_highest_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='highest_bid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
