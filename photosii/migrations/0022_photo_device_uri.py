# Generated by Django 3.2 on 2022-06-01 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photosii', '0021_alter_photo_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='device_uri',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
