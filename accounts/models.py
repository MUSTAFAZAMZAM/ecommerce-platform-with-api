from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
        ('O', 'آخر'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="تاريخ الميلاد")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="الجنس")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="الصورة الشخصية")
    bio = models.TextField(blank=True, verbose_name="نبذة شخصية")
    is_verified = models.BooleanField(default=False, verbose_name="محقق")
    email_notifications = models.BooleanField(default=True, verbose_name="إشعارات البريد الإلكتروني")
    sms_notifications = models.BooleanField(default=False, verbose_name="إشعارات الرسائل القصيرة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'منزل'),
        ('work', 'عمل'),
        ('other', 'آخر'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="المستخدم")
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home', verbose_name="نوع العنوان")
    first_name = models.CharField(max_length=50, verbose_name="الاسم الأول")
    last_name = models.CharField(max_length=50, verbose_name="الاسم الأخير")
    company = models.CharField(max_length=100, blank=True, verbose_name="الشركة")
    address_line_1 = models.CharField(max_length=200, verbose_name="العنوان الأول")
    address_line_2 = models.CharField(max_length=200, blank=True, verbose_name="العنوان الثاني")
    city = models.CharField(max_length=100, verbose_name="المدينة")
    state = models.CharField(max_length=100, verbose_name="المنطقة/الولاية")
    postal_code = models.CharField(max_length=20, verbose_name="الرمز البريدي")
    country = models.CharField(max_length=100, default='Saudi Arabia', verbose_name="الدولة")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    is_default = models.BooleanField(default=False, verbose_name="عنوان افتراضي")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "عنوان"
        verbose_name_plural = "العناوين"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, self.state, self.postal_code, self.country])
        return ", ".join(address_parts)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    name = models.CharField(max_length=100, default="قائمة الأمنيات", verbose_name="اسم القائمة")
    is_public = models.BooleanField(default=False, verbose_name="قائمة عامة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "قائمة أمنيات"
        verbose_name_plural = "قوائم الأمنيات"
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items', verbose_name="قائمة الأمنيات")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name="المنتج")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عنصر قائمة أمنيات"
        verbose_name_plural = "عناصر قوائم الأمنيات"
        unique_together = ['wishlist', 'product']

    def __str__(self):
        return f"{self.wishlist.name} - {self.product.name}"

