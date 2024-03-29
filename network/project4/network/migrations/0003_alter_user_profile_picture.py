# Generated by Django 3.2.6 on 2021-10-20 07:31

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_auto_20211019_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, null=True, quality=0, size=[200, 200], upload_to='images/'),
        ),
    ]
