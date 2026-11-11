from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CarMake(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    type = models.CharField(max_length=12, choices=[('SEDAN', 'Sedan'), ('SUV', 'SUV'), ('WAGON', 'Wagon')])
    year = models.PositiveIntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2023)])

    class Meta:
        unique_together = [('car_make', 'name', 'year')]

    def __str__(self):
        return f'{self.car_make.name} {self.name} ({self.year})'
