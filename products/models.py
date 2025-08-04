from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, verbose_name="وصف الفئة")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="صورة الفئة")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="الفئة الأب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "فئة"
        verbose_name_plural = "الفئات"
        ordering = ['name']

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم العلامة التجارية")
    description = models.TextField(blank=True, verbose_name="وصف العلامة التجارية")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="شعار العلامة التجارية")
    website = models.URLField(blank=True, verbose_name="موقع العلامة التجارية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "علامة تجارية"
        verbose_name_plural = "العلامات التجارية"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    description = models.TextField(verbose_name="وصف المنتج")
    short_description = models.CharField(max_length=500, blank=True, verbose_name="وصف مختصر")
    sku = models.CharField(max_length=100, unique=True, verbose_name="رمز المنتج")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="الفئة")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True, verbose_name="العلامة التجارية")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="سعر المقارنة")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="سعر التكلفة")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="كمية المخزون")
    low_stock_threshold = models.PositiveIntegerField(default=10, verbose_name="حد المخزون المنخفض")
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="الوزن (كجم)")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="الأبعاد")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_featured = models.BooleanField(default=False, verbose_name="منتج مميز")
    is_digital = models.BooleanField(default=False, verbose_name="منتج رقمي")
    requires_shipping = models.BooleanField(default=True, verbose_name="يتطلب شحن")
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان SEO")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="وصف SEO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="المنتج")
    image = models.ImageField(upload_to='products/', verbose_name="الصورة")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="النص البديل")
    is_primary = models.BooleanField(default=False, verbose_name="صورة رئيسية")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة منتج"
        verbose_name_plural = "صور المنتجات"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.product.name} - صورة {self.order}"

class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الخاصية")
    description = models.TextField(blank=True, verbose_name="وصف الخاصية")
    is_required = models.BooleanField(default=False, verbose_name="مطلوب")
    is_variation = models.BooleanField(default=False, verbose_name="خاصية متغيرة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "خاصية منتج"
        verbose_name_plural = "خصائص المنتجات"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, verbose_name="الخاصية")
    value = models.CharField(max_length=200, verbose_name="القيمة")
    color_code = models.CharField(max_length=7, blank=True, verbose_name="كود اللون")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "قيمة خاصية منتج"
        verbose_name_plural = "قيم خصائص المنتجات"
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations', verbose_name="المنتج")
    attributes = models.ManyToManyField(ProductAttributeValue, verbose_name="الخصائص")
    sku = models.CharField(max_length=100, unique=True, verbose_name="رمز التنويع")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="السعر")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="كمية المخزون")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تنويع منتج"
        verbose_name_plural = "تنويعات المنتجات"

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    @property
    def final_price(self):
        return self.price if self.price else self.product.price

