from django.contrib import admin
from .models import Famille, Categorie, UniteMesure, Fournisseur

admin.site.register(Famille)
admin.site.register(Categorie)
admin.site.register(UniteMesure)
admin.site.register(Fournisseur)