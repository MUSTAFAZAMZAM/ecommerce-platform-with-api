from rest_framework import serializers
from .models import Cart, CartItem, SavedForLater
from products.serializers import ProductListSerializer, ProductVariationSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variation = ProductVariationSerializer(read_only=True)
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variation', 'quantity', 'unit_price', 
            'total_price', 'is_available', 'added_at', 'updated_at'
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    total_weight = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'total_weight', 'created_at', 'updated_at']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variation_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("هذا المنتج غير متوفر حالياً.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("المنتج غير موجود.")
    
    def validate(self, data):
        from products.models import Product, ProductVariation
        
        product = Product.objects.get(id=data['product_id'])
        variation_id = data.get('variation_id')
        quantity = data['quantity']
        
        if variation_id:
            try:
                variation = ProductVariation.objects.get(id=variation_id, product=product, is_active=True)
                if variation.stock_quantity < quantity:
                    raise serializers.ValidationError(f"الكمية المطلوبة غير متوفرة. المتوفر: {variation.stock_quantity}")
            except ProductVariation.DoesNotExist:
                raise serializers.ValidationError("تنويع المنتج غير موجود.")
        else:
            if product.stock_quantity < quantity:
                raise serializers.ValidationError(f"الكمية المطلوبة غير متوفرة. المتوفر: {product.stock_quantity}")
        
        return data

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        cart_item = self.context.get('cart_item')
        if cart_item:
            if cart_item.variation:
                available_stock = cart_item.variation.stock_quantity
            else:
                available_stock = cart_item.product.stock_quantity
            
            if value > available_stock:
                raise serializers.ValidationError(f"الكمية المطلوبة غير متوفرة. المتوفر: {available_stock}")
        
        return value

class SavedForLaterSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variation = ProductVariationSerializer(read_only=True)
    
    class Meta:
        model = SavedForLater
        fields = ['id', 'product', 'variation', 'saved_at']

class SaveForLaterSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variation_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_product_id(self, value):
        from products.models import Product
        try:
            Product.objects.get(id=value, is_active=True)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("المنتج غير موجود.")

