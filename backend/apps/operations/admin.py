from django.contrib import admin
from .models import MouvementStock, Affectation, Consommation

admin.site.register(MouvementStock)
admin.site.register(Affectation)
admin.site.register(Consommation)
