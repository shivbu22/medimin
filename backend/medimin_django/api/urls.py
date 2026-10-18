from django.urls import path
from .views import (
    StatsView, CategoryListView, PharmacyListView, 
    AutocompleteView, SearchView, MedicineDetailView, RedirectView,
    PopularMedicinesView
)
from .webhooks import N8NCallbackView

urlpatterns = [
    path('stats/', StatsView.as_view(), name='stats'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('pharmacies/', PharmacyListView.as_view(), name='pharmacies'),
    path('autocomplete/', AutocompleteView.as_view(), name='autocomplete'),
    path('medicines/autocomplete/', AutocompleteView.as_view(), name='autocomplete-compat'),
    path('medicines/popular/', PopularMedicinesView.as_view(), name='popular-medicines'),
    path('search/', SearchView.as_view(), name='search'),
    path('medicines/<int:pk>/', MedicineDetailView.as_view(), name='medicine-detail-id'),
    path('medicines/<slug:slug>/', MedicineDetailView.as_view(), name='medicine-detail-slug'),
    path('redirect/<int:price_id>/', RedirectView.as_view(), name='redirect'),
    path('webhooks/n8n-complete/', N8NCallbackView.as_view(), name='n8n-callback'),
]
