from django.db import models

class Restaurent(models.Model):
    userID = models.CharField(max_length=255)
    placeID = models.CharField(max_length=255)
    rating = models.CharField(max_length=255)
    food_rating = models.CharField(max_length=255)
    service_rating = models.CharField(max_length=255)
    total_rating = models.CharField(max_length=255, null=True)

class Cusine(models.Model):
    placeID = models.CharField(max_length=255)
    cusine_type = models.CharField(max_length=255)
