# Generated by Django 4.1.7 on 2023-04-08 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.CharField(max_length=255)),
                ('placeID', models.CharField(max_length=255)),
                ('rating', models.CharField(max_length=255)),
                ('food_rating', models.CharField(max_length=255)),
                ('service_rating', models.CharField(max_length=255)),
            ],
        ),
    ]
