from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage, ProductAttribute, 
    ProductAttributeValue, ProductVariation
)

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent', 'is_active', 'children']
    
    def get_children(self, obj):
        if obj.category_set.exists():
            return CategorySerializer(obj.category_set.filter(is_active=True), many=True).data
        return []

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'logo', 'website', 'is_active']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    
    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value', 'color_code']

class ProductVariationSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    final_price = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariation
        fields = ['id', 'sku', 'price', 'stock_quantity', 'is_active', 'attributes', 'final_price']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'short_description', 'sku', 'category', 'category_name',
            'brand', 'brand_name', 'price', 'compare_price', 'is_active', 'is_featured',
            'primary_image', 'is_in_stock', 'discount_percentage', 'average_rating', 'review_count'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    rating_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'short_description', 'sku', 'category', 'brand',
            'price', 'compare_price', 'cost_price', 'stock_quantity', 'low_stock_threshold',
            'weight', 'dimensions', 'is_active', 'is_featured', 'is_digital', 'requires_shipping',
            'meta_title', 'meta_description', 'images', 'variations', 'is_in_stock', 'is_low_stock',
            'discount_percentage', 'average_rating', 'review_count', 'rating_distribution', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()
    
    def get_rating_distribution(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review.rating] += 1
        return distribution

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'short_description', 'sku', 'category', 'brand',
            'price', 'compare_price', 'cost_price', 'stock_quantity', 'low_stock_threshold',
            'weight', 'dimensions', 'is_active', 'is_featured', 'is_digital', 'requires_shipping',
            'meta_title', 'meta_description'
        ]
    
    def validate_sku(self, value):
        if self.instance and self.instance.sku == value:
            return value
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("منتج بهذا الرمز موجود بالفعل.")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("السعر يجب أن يكون أكبر من صفر.")
        return value

