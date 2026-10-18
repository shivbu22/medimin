from django.db.models import Q, Min, Max, Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from .models import Category, Medicine, Pharmacy, Price, PriceHistory, AnalyticsClick
from .serializers import (
    CategorySerializer, PharmacySerializer, MedicineBasicSerializer, 
    MedicineDetailSerializer, PriceSerializer, AutocompleteSerializer,
    SubstituteSerializer
)
from django.utils import timezone
import math
import requests
from django.conf import settings

class StatsView(APIView):
    def get(self, request):
        med_count = Medicine.objects.count()
        pharm_count = Pharmacy.objects.filter(is_active=True).count()
        price_count = Price.objects.count()
        cat_count = Category.objects.count()

        disc = Price.objects.filter(in_stock=True).aggregate(
            avg_savings=Avg('discount_percentage'),
            max_savings=Max('discount_percentage')
        )
        
        return Response({
            "total_medicines": med_count,
            "total_pharmacies": pharm_count,
            "total_prices": price_count,
            "avg_savings_percentage": round(disc['avg_savings'] or 0, 1),
            "max_savings_percentage": round(disc['max_savings'] or 0, 1),
            "categories_count": cat_count
        })

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all().order_by('name')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class PharmacyListView(APIView):
    def get(self, request):
        pharmacies = Pharmacy.objects.filter(is_active=True).order_by('-rating')
        serializer = PharmacySerializer(pharmacies, many=True)
        return Response(serializer.data)

class AutocompleteView(APIView):
    def get(self, request):
        q = request.query_params.get('q', '')
        if not q:
            return Response([])
        
        medicines = Medicine.objects.filter(
            Q(name__icontains=q) | 
            Q(active_salt__icontains=q) | 
            Q(manufacturer__icontains=q)
        ).order_by('name')[:10]
        
        serializer = AutocompleteSerializer(medicines, many=True)
        return Response(serializer.data)

class SearchView(APIView):
    def get(self, request):
        q = request.query_params.get('q', '')
        category_slug = request.query_params.get('category')
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 20))
        except (ValueError, TypeError):
            return Response({"error": "Invalid pagination parameters"}, status=status.HTTP_400_BAD_REQUEST)

        if not q:
            return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Medicine.objects.filter(
            Q(name__icontains=q) | 
            Q(active_salt__icontains=q) | 
            Q(manufacturer__icontains=q)
        )

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        total = queryset.count()
        
        # Annotate with price info
        offset = (page - 1) * limit
        results_qs = queryset.annotate(
            lowest_price=Min('prices__selling_price', filter=Q(prices__in_stock=True)),
            highest_price=Max('prices__selling_price', filter=Q(prices__in_stock=True)),
            pharmacy_count=Count('prices', distinct=True, filter=Q(prices__in_stock=True))
        ).order_by('name')[offset:offset+limit]

        results = []
        for med in results_qs:
            # Check for cheaper substitutes
            cheapest_sub = Medicine.objects.filter(
                active_salt=med.active_salt
            ).exclude(id=med.id).aggregate(
                min_price=Min('prices__selling_price', filter=Q(prices__in_stock=True))
            )['min_price']

            has_cheaper = False
            cheapest_sub_price = None
            if cheapest_sub is not None and med.lowest_price is not None:
                if cheapest_sub < med.lowest_price:
                    has_cheaper = True
                    cheapest_sub_price = round(cheapest_sub, 2)

            med_data = MedicineBasicSerializer(med).data
            med_data.update({
                "lowest_price": med.lowest_price,
                "highest_price": med.highest_price,
                "pharmacy_count": med.pharmacy_count,
                "has_cheaper_substitute": has_cheaper,
                "cheapest_substitute_price": cheapest_sub_price
            })
            results.append(med_data)

        # Trigger n8n webhook if no results found
        if total == 0 and settings.N8N_WEBHOOK_URL:
            try:
                # We do this asynchronously in a real app, 
                # but here we'll just send it with a short timeout
                requests.post(
                    settings.N8N_WEBHOOK_URL, 
                    json={"query": q, "timestamp": timezone.now().isoformat()},
                    timeout=1
                )
            except Exception as e:
                print(f"Failed to trigger n8n webhook: {e}")

        total_pages = max(1, math.ceil(total / limit))

        return Response({
            "query": q,
            "results": results,
            "count": total,
            "total_pages": total_pages,
            "page": page,
            "syncing": total == 0 # Tell frontend we are looking for this
        })

class MedicineDetailView(APIView):
    def get(self, request, pk=None, slug=None):
        if pk:
            medicine = get_object_or_404(Medicine, pk=pk)
        elif slug:
            medicine = get_object_or_404(Medicine, slug=slug)
        else:
            return Response({"error": "ID or slug required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get prices sorted cheapest first
        prices_qs = Price.objects.filter(medicine=medicine).select_related('pharmacy').order_by('selling_price')
        
        # Calculate savings
        price_list = list(prices_qs)
        max_price = 0
        if price_list:
            max_price = max(p.selling_price for p in price_list)
            for p in price_list:
                p.savings = round(max_price - p.selling_price, 2)

        # Get substitutes
        substitutes_qs = Medicine.objects.filter(
            active_salt=medicine.active_salt
        ).exclude(id=medicine.id).annotate(
            lowest_p=Min('prices__selling_price', filter=Q(prices__in_stock=True))
        )
        
        substitutes = []
        for sub in substitutes_qs:
            price_diff = None
            if sub.lowest_p and price_list and price_list[0].selling_price:
                price_diff = ((sub.lowest_p - price_list[0].selling_price) / price_list[0].selling_price) * 100
            
            substitutes.append({
                "id": sub.id,
                "name": sub.name,
                "slug": sub.slug,
                "manufacturer": sub.manufacturer,
                "lowest_price": sub.lowest_p,
                "price_diff_percentage": round(price_diff, 1) if price_diff is not None else None
            })

        # Serializers
        med_serializer = MedicineDetailSerializer(medicine)
        price_serializer = PriceSerializer(price_list, many=True)
        
        cheapest = price_serializer.data[0] if price_serializer.data else None
        most_expensive = price_serializer.data[-1] if price_serializer.data else None
        
        max_savings_pct = 0
        if price_list and max_price > 0:
            min_price = price_list[0].selling_price
            max_savings_pct = ((max_price - min_price) / max_price) * 100

        # Check for price staleness (Just-in-Time Sync)
        is_syncing = medicine.is_syncing
        last_price_update = Price.objects.filter(medicine=medicine).aggregate(Max('updated_at'))['updated_at__max']
        
        # Define stale as > 1 hour
        stale_threshold = timezone.now() - timezone.timedelta(hours=1)
        
        if (not last_price_update or last_price_update < stale_threshold) and not is_syncing:
            if settings.N8N_WEBHOOK_URL:
                try:
                    # Mark as syncing to avoid duplicate triggers
                    medicine.is_syncing = True
                    medicine.save()
                    is_syncing = True
                    
                    requests.post(
                        settings.N8N_WEBHOOK_URL, 
                        json={
                            "query": medicine.name, 
                            "type": "refresh",
                            "timestamp": timezone.now().isoformat()
                        },
                        headers={
                            "X-Webhook-Secret": settings.MEDIMIN_WEBHOOK_SECRET
                        },
                        timeout=1
                    )
                except Exception as e:
                    print(f"Failed to trigger sync for {medicine.name}: {e}")
                    medicine.is_syncing = False
                    medicine.save()

        return Response({
            "medicine": med_serializer.data,
            "prices": price_serializer.data,
            "cheapest": cheapest,
            "most_expensive": most_expensive,
            "max_savings_percentage": round(max_savings_pct, 1),
            "substitutes": substitutes,
            "is_syncing": is_syncing,
            "last_updated": last_price_update
        })

class PopularMedicinesView(APIView):
    def get(self, request):
        # Optimization: Fetch a batch and sample in memory instead of 'order_by(?)' on 254k rows
        total = Medicine.objects.count()
        import random
        # Pick 100 random medicines and take 8 from them (to avoid expensive random sort of entire DB)
        random_indices = random.sample(range(total), min(total, 50))
        medicines = Medicine.objects.filter(id__in=random_indices).annotate(
            lowest_price=Min('prices__selling_price', filter=Q(prices__in_stock=True))
        )[:8]
        
        serializer = MedicineBasicSerializer(medicines, many=True)
        results = []
        for i, med in enumerate(serializer.data):
            med['lowest_price'] = medicines[i].lowest_price
            results.append(med)
            
        return Response(results)

class RedirectView(APIView):
    def get(self, request, price_id):
        price = get_object_or_404(Price.objects.select_related('medicine', 'pharmacy'), pk=price_id)
        
        # Log click
        AnalyticsClick.objects.create(
            medicine=price.medicine,
            pharmacy=price.pharmacy,
            session_id=request.query_params.get('sid'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        if not price.product_url:
            # Fallback to pharmacy main website if product URL is missing
            return redirect(price.pharmacy.website_url)
            
        return redirect(price.product_url)
