from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from .models import Targy
from django.utils import timezone

class RegisgboltTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.arverezo = User.objects.create_user(username='arverezo', password='password', is_staff=True)
        
        arverezo_group, _ = Group.objects.get_or_create(name='Arverezo')
        self.arverezo.groups.add(arverezo_group)

        self.targy = Targy.objects.create(
            megnevezes="Teszt Festmény", 
            indulo_ar=1000, 
            aktualis_ar=1000,
            arveres_ideje=timezone.now()
        )
        self.client = Client()

    def test_termek_list_view(self):
        """1. teszt: A termékek oldal betöltődik és listázza a tárgyat"""
        response = self.client.get('/termekek/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teszt Festmény")

    def test_licit_requires_login(self):
        """2. teszt: Nem bejelentkezett felhasználó nem tud licitálni (átirányítás loginra)"""
        self.targy.licit_aktiv = True
        self.targy.save()
        response = self.client.post(f'/termekek/{self.targy.pk}/licit/', {'licit_osszeg': 2000})
        self.assertEqual(response.status_code, 302) 
        self.targy.refresh_from_db()
        self.assertEqual(self.targy.aktualis_ar, 1000)

    def test_licit_success(self):
        """3. teszt: Sikeres licitálás bejelentkezve"""
        self.client.login(username='testuser', password='password')
        self.targy.licit_aktiv = True
        self.targy.save()
        
        response = self.client.post(f'/termekek/{self.targy.pk}/licit/', {'licit_osszeg': 1500})
        self.targy.refresh_from_db()
        
        self.assertEqual(self.targy.aktualis_ar, 1500)
        self.assertEqual(self.targy.nyertes, self.user)

    def test_licit_rejects_lower_bid(self):
        """4. teszt: Az aktuális árnál alacsonyabb vagy egyenlő licit elutasítása"""
        self.client.login(username='testuser', password='password')
        self.targy.licit_aktiv = True
        self.targy.save()

        self.client.post(f'/termekek/{self.targy.pk}/licit/', {'licit_osszeg': 900})
        self.targy.refresh_from_db()
        self.assertEqual(self.targy.aktualis_ar, 1000)

    def test_arveres_lezarasa_by_arverezo(self):
        """5. teszt: Csak az árverező tudja lezárni a licitet"""
        self.client.login(username='arverezo', password='password')
        self.targy.licit_aktiv = True
        self.targy.save()

        response = self.client.get(f'/termekek/{self.targy.pk}/stop/')
        self.targy.refresh_from_db()

        self.assertFalse(self.targy.licit_aktiv)
        self.assertTrue(self.targy.lezart)