from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="المستخدم")
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name="مفتاح الجلسة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سلة تسوق"
        verbose_name_plural = "سلال التسوق"

    def __str__(self):
        if self.user:
            return f"سلة {self.user.username}"
        return f"سلة ضيف {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_weight(self):
        total = Decimal('0.00')
        for item in self.items.all():
            if item.product.weight:
                total += item.product.weight * item.quantity
        return total

    def clear(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="السلة")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="المنتج")
    variation = models.ForeignKey('products.ProductVariation', on_delete=models.CASCADE, blank=True, null=True, verbose_name="التنويع")
    quantity = models.PositiveIntegerField(default=1, verbose_name="الكمية")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عنصر سلة تسوق"
        verbose_name_plural = "عناصر سلة التسوق"
        unique_together = ['cart', 'product', 'variation']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def unit_price(self):
        if self.variation:
            return self.variation.final_price
        return self.product.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def is_available(self):
        if self.variation:
            return self.variation.stock_quantity >= self.quantity
        return self.product.stock_quantity >= self.quantity

class SavedForLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="المنتج")
    variation = models.ForeignKey('products.ProductVariation', on_delete=models.CASCADE, blank=True, null=True, verbose_name="التنويع")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محفوظ للاحقاً"
        verbose_name_plural = "محفوظات للاحقاً"
        unique_together = ['user', 'product', 'variation']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

