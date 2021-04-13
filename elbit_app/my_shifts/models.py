from django.db import models
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User


# Create your models here.

class WorkerProfileInfo(models.Model):
    worker = models.OneToOneField(User, on_delete=models.CASCADE)

    # additional attrs
    worker_number = models.IntegerField(primary_key=True, blank=True, unique=True)
    gate_worker = models.BooleanField(default=False, blank=True)
    city_address = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.worker.username

    def is_valid(self):
        return 99999 < self.worker_number < 10000000


class Shift(models.Model):
    user = models.ForeignKey(User, related_name='worker_shift', default=None,
                             on_delete=models.CASCADE, )
    date = models.DateField(default=None)
    shift_time = models.CharField(max_length=256, default=None)
    capacity = models.PositiveIntegerField(default=5)
    value = models.PositiveIntegerField(default=0)
    creation_time = models.PositiveIntegerField(default=0)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.date.__str__() + ' ' + self.shift_time
