from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('confirmed', 'مؤكد'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
        ('refunded', 'مسترد'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('paid', 'مدفوع'),
        ('failed', 'فشل'),
        ('refunded', 'مسترد'),
        ('partially_refunded', 'مسترد جزئياً'),
    ]

    order_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الطلب")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="المستخدم")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    
    # Billing Address
    billing_first_name = models.CharField(max_length=50, verbose_name="الاسم الأول للفاتورة")
    billing_last_name = models.CharField(max_length=50, verbose_name="الاسم الأخير للفاتورة")
    billing_company = models.CharField(max_length=100, blank=True, verbose_name="شركة الفاتورة")
    billing_address_line_1 = models.CharField(max_length=200, verbose_name="عنوان الفاتورة الأول")
    billing_address_line_2 = models.CharField(max_length=200, blank=True, verbose_name="عنوان الفاتورة الثاني")
    billing_city = models.CharField(max_length=100, verbose_name="مدينة الفاتورة")
    billing_state = models.CharField(max_length=100, verbose_name="منطقة الفاتورة")
    billing_postal_code = models.CharField(max_length=20, verbose_name="الرمز البريدي للفاتورة")
    billing_country = models.CharField(max_length=100, verbose_name="دولة الفاتورة")
    
    # Shipping Address
    shipping_first_name = models.CharField(max_length=50, verbose_name="الاسم الأول للشحن")
    shipping_last_name = models.CharField(max_length=50, verbose_name="الاسم الأخير للشحن")
    shipping_company = models.CharField(max_length=100, blank=True, verbose_name="شركة الشحن")
    shipping_address_line_1 = models.CharField(max_length=200, verbose_name="عنوان الشحن الأول")
    shipping_address_line_2 = models.CharField(max_length=200, blank=True, verbose_name="عنوان الشحن الثاني")
    shipping_city = models.CharField(max_length=100, verbose_name="مدينة الشحن")
    shipping_state = models.CharField(max_length=100, verbose_name="منطقة الشحن")
    shipping_postal_code = models.CharField(max_length=20, verbose_name="الرمز البريدي للشحن")
    shipping_country = models.CharField(max_length=100, verbose_name="دولة الشحن")
    
    # Order Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="حالة الطلب")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="حالة الدفع")
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المجموع الفرعي")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="مبلغ الضريبة")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="تكلفة الشحن")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="مبلغ الخصم")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ الإجمالي")
    
    # Additional Info
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name="رقم التتبع")
    shipped_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الشحن")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ التسليم")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ['-created_at']

    def __str__(self):
        return f"طلب #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        import random
        import string
        return ''.join(random.choices(string.digits, k=8))

    @property
    def billing_full_name(self):
        return f"{self.billing_first_name} {self.billing_last_name}"

    @property
    def shipping_full_name(self):
        return f"{self.shipping_first_name} {self.shipping_last_name}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="الطلب")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="المنتج")
    variation = models.ForeignKey('products.ProductVariation', on_delete=models.CASCADE, blank=True, null=True, verbose_name="التنويع")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر الإجمالي")
    
    # Store product details at time of order
    product_name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    product_sku = models.CharField(max_length=100, verbose_name="رمز المنتج")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلبات"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name="الطلب")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="تم الإنشاء بواسطة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تاريخ حالة الطلب"
        verbose_name_plural = "تاريخ حالات الطلبات"
        ordering = ['-created_at']

    def __str__(self):
        return f"طلب #{self.order.order_number} - {self.get_status_display()}"

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'نسبة مئوية'),
        ('fixed', 'مبلغ ثابت'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="كود الكوبون")
    name = models.CharField(max_length=100, verbose_name="اسم الكوبون")
    description = models.TextField(blank=True, verbose_name="وصف الكوبون")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, verbose_name="نوع الخصم")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قيمة الخصم")
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="الحد الأدنى للمبلغ")
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="الحد الأقصى للخصم")
    usage_limit = models.PositiveIntegerField(blank=True, null=True, verbose_name="حد الاستخدام")
    used_count = models.PositiveIntegerField(default=0, verbose_name="عدد مرات الاستخدام")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    valid_from = models.DateTimeField(verbose_name="صالح من")
    valid_until = models.DateTimeField(verbose_name="صالح حتى")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "كوبون خصم"
        verbose_name_plural = "كوبونات الخصم"

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_until and
                (self.usage_limit is None or self.used_count < self.usage_limit))

    def calculate_discount(self, amount):
        if not self.is_valid or amount < self.minimum_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
        else:
            discount = self.discount_value
        
        if self.maximum_discount:
            discount = min(discount, self.maximum_discount)
        
        return discount

