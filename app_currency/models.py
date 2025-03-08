from django.db import models

class Currency(models.Model):
    objects = None
    currency = models.CharField(max_length=10, unique=True)
    buy = models.DecimalField(max_digits=10, decimal_places=2)
    sell = models.DecimalField(max_digits=10, decimal_places=2)
    nbt = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.currency
