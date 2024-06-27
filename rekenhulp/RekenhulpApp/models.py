from django.core.validators import RegexValidator
from django.db import models

alpha = RegexValidator("[A-Za-zÀ-ȕ]", 'Only alphabetic characters')


class Sondevoeding(models.Model):
    Soort = models.CharField(primary_key=True, max_length=50,
                             validators=[alpha])
    Energie = models.DecimalField(max_digits=5, decimal_places=0)
    Eiwit = models.DecimalField(max_digits=5, decimal_places=1)
    Vezels = models.DecimalField(max_digits=5, decimal_places=1)
    Zout = models.DecimalField(max_digits=5, decimal_places=2)
    Natrium = models.DecimalField(max_digits=5, decimal_places=0)
    Vocht = models.DecimalField(max_digits=5, decimal_places=0)

    class Meta:
        db_table = 'sondevoeding'

    def __str__(self):
        return self.Soort