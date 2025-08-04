from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('<int:pk>/related/', views.RelatedProductsView.as_view(), name='related-products'),
    
    # Search and Filters
    path('search/suggestions/', views.product_search_suggestions, name='search-suggestions'),
    path('filters/', views.product_filters, name='product-filters'),
    
    # Admin endpoints
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
]

