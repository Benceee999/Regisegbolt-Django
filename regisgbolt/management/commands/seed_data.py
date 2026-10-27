from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from regisgbolt.models import Targy, Velemeny

class Command(BaseCommand):
    help = "Feltölti az adatbázist kezdeti adatokkal (felhasználók, csoportok, tárgyak, vélemények)."

    def handle(self, *args, **options):
        self.stdout.write("Adatbázis feltöltése folyamatban...")

        arverezo_group, _ = Group.objects.get_or_create(name="Arverezo")

        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser("admin", "admin@aukcio.hu", "admin123")
            admin_user.groups.add(arverezo_group)
            self.stdout.write(self.style.SUCCESS("Szuperadmin létrehozva (admin / admin123)"))
        else:
            admin_user = User.objects.get(username="admin")
            admin_user.groups.add(arverezo_group)

        if not User.objects.filter(username="arverezo").exists():
            arv_user = User.objects.create_user("arverezo", "arverezo@aukcio.hu", "arverezo123", is_staff=True)
            arv_user.groups.add(arverezo_group)
            self.stdout.write(self.style.SUCCESS("Árverező fiók létrehozva (arverezo / arverezo123)"))

        if not User.objects.filter(username="licitalo").exists():
            User.objects.create_user("licitalo", "vevo@freemail.hu", "licit123")
            self.stdout.write(self.style.SUCCESS("Normál felhasználó létrehozva (licitalo / licit123)"))

        if not Targy.objects.exists():
            now = timezone.now()
            targyak = [
                Targy(
                    megnevezes="Csontváry Kosztka Tivadar - Magányos cédrus (Reprodukció)",
                    indulo_ar=150000,
                    aktualis_ar=150000,
                    licit_aktiv=True,
                    lezart=False,
                    arveres_ideje=now + timedelta(days=2),
                    kep_fajlnev="cedrus.jpg"
                ),
                Targy(
                    megnevezes="Zsolnay aranyozott eozinmázas teáskészlet (1920)",
                    indulo_ar=45000,
                    aktualis_ar=45000,
                    licit_aktiv=False,
                    lezart=False,
                    arveres_ideje=now + timedelta(days=5),
                    kep_fajlnev="zsolnay.jpg"
                ),
                Targy(
                    megnevezes="Viktória-korabeli zafír és gyémánt berakásos gyűrű",
                    indulo_ar=95000,
                    aktualis_ar=110000,
                    licit_aktiv=True,
                    lezart=False,
                    arveres_ideje=now + timedelta(days=1),
                    kep_fajlnev="gyuru.jpg"
                ),
                Targy(
                    megnevezes="Herendi Viktória mintás porcelán díszváza",
                    indulo_ar=35000,
                    aktualis_ar=60000,
                    licit_aktiv=False,
                    lezart=True,
                    nyertes=admin_user,
                    arveres_ideje=now - timedelta(days=1),
                    kep_fajlnev="herendi.jpg"
                ),
            ]
            Targy.objects.bulk_create(targyak)
            self.stdout.write(self.style.SUCCESS("Minta műtárgyak sikeresen létrehozva (aktív, licitálható és lezárt tételek)."))
        else:
            self.stdout.write("Már léteznek műtárgyak az adatbázisban, a tárgylétrehozás átugorva.")

        if not Velemeny.objects.exists():
            Velemeny.objects.create(
                nev="Horváth Béla",
                email="bela@pelda.hu",
                uzenet="Kiváló állapotban érkezett meg a megnyert festmény, profi csomagolás és ügyintézés!"
            )
            Velemeny.objects.create(
                nev="Kovács Katalin",
                email="kata@pelda.hu",
                uzenet="Régóta kerestem már ezt a Herendi porcelánt. Köszönöm a rugalmas aukciót!"
            )
            self.stdout.write(self.style.SUCCESS("Minta vélemények rögzítve."))

        self.stdout.write(self.style.SUCCESS("Az adatbázis készen áll a bemutatásra!"))