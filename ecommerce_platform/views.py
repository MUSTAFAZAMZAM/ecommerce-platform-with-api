from django.shortcuts import render
from products.models import Product, Category

def home(request):
    """
    عرض الصفحة الرئيسية
    """
    # المنتجات المميزة
    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('category', 'brand')[:8]
    
    # الفئات الرئيسية
    main_categories = Category.objects.filter(
        is_active=True, 
        parent=None
    )[:8]
    
    context = {
        'featured_products': featured_products,
        'main_categories': main_categories,
    }
    
    return render(request, 'home.html', context)

