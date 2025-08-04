from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import Category, Brand, Product
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer, 
    ProductDetailSerializer, ProductCreateUpdateSerializer
)

class CategoryListView(generics.ListAPIView):
    """
    API endpoint لعرض قائمة الفئات
    """
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint لعرض تفاصيل فئة محددة
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class BrandListView(generics.ListAPIView):
    """
    API endpoint لعرض قائمة العلامات التجارية
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer

class ProductListView(generics.ListAPIView):
    """
    API endpoint لعرض قائمة المنتجات مع إمكانية البحث والفلترة
    """
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured']
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # فلترة حسب السعر
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # فلترة المنتجات المتوفرة فقط
        in_stock_only = self.request.query_params.get('in_stock_only')
        if in_stock_only and in_stock_only.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        # فلترة حسب التقييم
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            # هذا يتطلب تعديل أكثر تعقيداً للاستعلام
            pass
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    """
    API endpoint لعرض تفاصيل منتج محدد
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer

class FeaturedProductsView(generics.ListAPIView):
    """
    API endpoint لعرض المنتجات المميزة
    """
    queryset = Product.objects.filter(is_active=True, is_featured=True)
    serializer_class = ProductListSerializer

class RelatedProductsView(generics.ListAPIView):
    """
    API endpoint لعرض المنتجات ذات الصلة
    """
    serializer_class = ProductListSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            # المنتجات ذات الصلة من نفس الفئة أو العلامة التجارية
            related_products = Product.objects.filter(
                Q(category=product.category) | Q(brand=product.brand),
                is_active=True
            ).exclude(id=product_id)[:8]
            return related_products
        except Product.DoesNotExist:
            return Product.objects.none()

@api_view(['GET'])
def product_search_suggestions(request):
    """
    API endpoint لاقتراحات البحث
    """
    query = request.GET.get('q', '')
    if len(query) < 2:
        return Response([])
    
    # البحث في أسماء المنتجات
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('id', 'name')[:5]
    
    # البحث في الفئات
    categories = Category.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('id', 'name')[:3]
    
    # البحث في العلامات التجارية
    brands = Brand.objects.filter(
        name__icontains=query,
        is_active=True
    ).values('id', 'name')[:3]
    
    suggestions = {
        'products': list(products),
        'categories': list(categories),
        'brands': list(brands)
    }
    
    return Response(suggestions)

@api_view(['GET'])
def product_filters(request):
    """
    API endpoint لإرجاع خيارات الفلترة المتاحة
    """
    category_id = request.GET.get('category')
    
    # بناء الاستعلام الأساسي
    queryset = Product.objects.filter(is_active=True)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    # نطاق الأسعار
    price_range = queryset.aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    # العلامات التجارية المتاحة
    brands = Brand.objects.filter(
        product__in=queryset,
        is_active=True
    ).distinct().values('id', 'name')
    
    # الفئات المتاحة (إذا لم يتم تحديد فئة)
    categories = []
    if not category_id:
        categories = Category.objects.filter(
            product__in=queryset,
            is_active=True
        ).distinct().values('id', 'name')
    
    filters = {
        'price_range': price_range,
        'brands': list(brands),
        'categories': list(categories)
    }
    
    return Response(filters)

# Admin Views (تتطلب صلاحيات إدارية)
class ProductCreateView(generics.CreateAPIView):
    """
    API endpoint لإنشاء منتج جديد (للإدارة)
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    # permission_classes = [IsAdminUser]  # سيتم إضافتها لاحقاً

class ProductUpdateView(generics.UpdateAPIView):
    """
    API endpoint لتحديث منتج (للإدارة)
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    # permission_classes = [IsAdminUser]  # سيتم إضافتها لاحقاً

class ProductDeleteView(generics.DestroyAPIView):
    """
    API endpoint لحذف منتج (للإدارة)
    """
    queryset = Product.objects.all()
    # permission_classes = [IsAdminUser]  # سيتم إضافتها لاحقاً

