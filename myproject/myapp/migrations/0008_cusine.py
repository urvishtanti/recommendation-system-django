# Generated by Django 4.1.7 on 2023-04-08 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_restaurent_delete_mymodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='cusine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placeID', models.CharField(max_length=255)),
                ('cusine_type', models.CharField(max_length=255)),
            ],
        ),
    ]
