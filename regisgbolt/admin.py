import os
from django.contrib import admin
from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Targy, Velemeny

class TargyAdminForm(forms.ModelForm):
    kep_feltoltes = forms.ImageField(
        required=False, 
        label="Kép feltöltése", 
        help_text="Válassz ki egy képet! A rendszer automatikusan kimenti és beállítja a nevét."
    )

    class Meta:
        model = Targy
        fields = '__all__'

    def save(self, commit=True):
        targy = super().save(commit=False)
        
        kep = self.cleaned_data.get('kep_feltoltes')
        if kep:
            save_dir = os.path.join(settings.BASE_DIR, 'regisgbolt', 'static', 'Termek_images')
            
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            fs = FileSystemStorage(location=save_dir)
            filename = fs.save(kep.name, kep)
            
            targy.kep_fajlnev = filename

        if commit:
            targy.save()
        return targy

@admin.register(Targy)
class TargyAdmin(admin.ModelAdmin):
    form = TargyAdminForm
    list_display = ('megnevezes', 'indulo_ar', 'aktualis_ar', 'licit_aktiv', 'lezart', 'nyertes', 'arveres_ideje')
    list_filter = ('lezart', 'licit_aktiv', 'nyertes')
    search_fields = ('megnevezes',)

    readonly_fields = ('aktualis_ar', 'kep_fajlnev')

@admin.register(Velemeny)
class VelemenyAdmin(admin.ModelAdmin):
    list_display = ('nev', 'email', 'kuldes_datuma')