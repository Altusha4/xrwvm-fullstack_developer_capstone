from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel


class Command(BaseCommand):
    help = 'Seed demonstration makes and models without deleting data'

    def handle(self, *args, **kwargs):
        for make, model, kind, year in [('Toyota', 'Camry', 'SEDAN', 2021), ('Honda', 'CR-V', 'SUV', 2022), ('Subaru', 'Outback', 'WAGON', 2020)]:
            obj, _ = CarMake.objects.get_or_create(name=make)
            CarModel.objects.get_or_create(car_make=obj, name=model, year=year, defaults={'type': kind})
        self.stdout.write('Car models ready')
