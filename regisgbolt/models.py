from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class Targy(models.Model):
    TIPUSOK = [
        ("festmeny", "Festmény"),
        ("ekszer", "Ékszer"),
        ("porcelan", "Porcelán"),
    ]
    megnevezes = models.CharField(max_length=200, db_column="Nev")
    indulo_ar = models.DecimalField(max_digits=12, decimal_places=0, db_column="Indulo_ar")
    
    aktualis_ar = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, help_text="A jelenlegi legmagasabb licit")
    nyertes = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="nyert_targyak")
    licit_aktiv = models.BooleanField(default=False, verbose_name="Licitálás aktív")
    lezart = models.BooleanField(default=False, verbose_name="Árverés lezárva")
    
    arveres_ideje = models.DateTimeField(db_column="Arveres_ideje")

    kep_fajlnev = models.CharField(
        max_length=255,
        db_column="Kep_url",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        help_text="Automatikusan töltődik ki a feltöltött kép nevével."
    )

    class Meta:
        db_table = "Termekek"
        permissions = [
            ("can_manage_auction", "Kezelheti az árverést (indítás/lezárás)"),
        ]

    def __str__(self):
        return self.megnevezes

    @property
    def kep_relpath(self) -> str:
        if not self.kep_fajlnev:
            return "regisgbolt/img/placeholder.png"
        return f"Termek_images/{self.kep_fajlnev}"

    def save(self, *args, **kwargs):
        if self.aktualis_ar is None:
            self.aktualis_ar = self.indulo_ar
        if self.kep_fajlnev:
            self.kep_fajlnev = self.kep_fajlnev.strip()
        super().save(*args, **kwargs)

class Velemeny(models.Model):
    nev = models.CharField("Név", max_length=100)
    email = models.EmailField("E-mail cím", blank=True)
    uzenet = models.TextField("Vélemény")
    kuldes_datuma = models.DateTimeField("Küldés dátuma", auto_now_add=True)

    class Meta:
        ordering = ["-kuldes_datuma"]
        verbose_name = "vélemény"
        verbose_name_plural = "vélemények"

    def __str__(self):
        return f"{self.nev} - {self.kuldes_datuma:%Y.%m.%d %H:%M}"