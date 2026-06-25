from django.contrib import admin
from .models import Magasin, Materiel, Consommable

admin.site.register(Materiel)
admin.site.register(Magasin)
admin.site.register(Consommable)
