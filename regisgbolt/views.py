from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Targy, Velemeny
from .forms import VelemenyForm

def is_arverezo(user):
    return user.is_authenticated and user.is_active and (
        user.is_superuser or user.groups.filter(name='Arverezo').exists()
    )

class IndexView(TemplateView):
    template_name = "index.html"

class MunkatarsainkView(TemplateView):
    template_name = "munkatarsaink.html"

class ElerhetosegView(CreateView):
    model = Velemeny
    form_class = VelemenyForm
    template_name = "elerhetoseg.html"
    success_url = reverse_lazy("elerhetoseg")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["velemenyek"] = Velemeny.objects.all()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Köszönjük a véleményedet!")
        return super().form_valid(form)

class TermekekListView(ListView):
    model = Targy
    template_name = "termekek.html"
    context_object_name = "targyak"
    paginate_by = 3
    ordering = ["arveres_ideje"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(megnevezes__icontains=q) | Q(aktualis_ar__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["is_arverezo"] = is_arverezo(self.request.user)
        return context

class TermekDetailView(DetailView):
    model = Targy
    template_name = "termek_reszlet.html"
    context_object_name = "targy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_arverezo"] = is_arverezo(self.request.user)
        return context

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def licit_tetel(request, pk):
    targy = get_object_or_404(Targy, pk=pk)
    
    if request.method == "POST":
        if not targy.licit_aktiv or targy.lezart:
            messages.error(request, "Erre a tárgyra jelenleg nem lehet licitálni.")
            return redirect("termek_reszlet", pk=pk)

        try:
            licit_osszeg = int(request.POST.get("licit_osszeg"))
            min_licit = targy.aktualis_ar + 1
            
            if licit_osszeg < min_licit:
                messages.error(request, f"A licitnek nagyobbnak kell lennie, mint {targy.aktualis_ar} Ft.")
            else:
                targy.aktualis_ar = licit_osszeg
                targy.nyertes = request.user
                targy.save()
                messages.success(request, f"Sikeres licit: {licit_osszeg} Ft!")
        except (ValueError, TypeError):
            messages.error(request, "Érvénytelen összeg.")
            
    return redirect("termek_reszlet", pk=pk)

@user_passes_test(is_arverezo)
def arveres_inditasa(request, pk):
    targy = get_object_or_404(Targy, pk=pk)
    if not targy.lezart:
        targy.licit_aktiv = True
        targy.save()
        messages.info(request, "Az árverés elindult!")
    return redirect("termek_reszlet", pk=pk)

@user_passes_test(is_arverezo)
def arveres_lezarasa(request, pk):
    targy = get_object_or_404(Targy, pk=pk)
    if targy.licit_aktiv:
        targy.licit_aktiv = False
        targy.lezart = True
        targy.save()
        messages.success(request, f"Az árverés lezárult. Nyertes: {targy.nyertes} - Ár: {targy.aktualis_ar} Ft")
    return redirect("termek_reszlet", pk=pk)

def custom_page_not_found_view(request, exception):
    return render(request, "404.html", {}, status=404)