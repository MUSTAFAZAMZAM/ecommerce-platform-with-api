from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('credit_card', 'بطاقة ائتمان'),
        ('debit_card', 'بطاقة خصم'),
        ('bank_transfer', 'تحويل بنكي'),
        ('cash_on_delivery', 'الدفع عند الاستلام'),
        ('digital_wallet', 'محفظة رقمية'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم طريقة الدفع")
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name="نوع الدفع")
    description = models.TextField(blank=True, verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="نسبة رسوم المعالجة")
    processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="رسوم المعالجة الثابتة")
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="الحد الأدنى للمبلغ")
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="الحد الأقصى للمبلغ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "طريقة دفع"
        verbose_name_plural = "طرق الدفع"
        ordering = ['name']

    def __str__(self):
        return self.name

    def calculate_processing_fee(self, amount):
        percentage_fee = amount * (self.processing_fee_percentage / 100)
        return percentage_fee + self.processing_fee_fixed

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
        ('refunded', 'مسترد'),
        ('partially_refunded', 'مسترد جزئياً'),
    ]

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments', verbose_name="الطلب")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="طريقة الدفع")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="رسوم المعالجة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="معرف المعاملة")
    gateway_response = models.JSONField(blank=True, null=True, verbose_name="استجابة البوابة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ المعالجة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"
        ordering = ['-created_at']

    def __str__(self):
        return f"دفعة #{self.id} - طلب #{self.order.order_number}"

    @property
    def total_amount(self):
        return self.amount + self.processing_fee

class Refund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
    ]

    REASON_CHOICES = [
        ('customer_request', 'طلب العميل'),
        ('defective_product', 'منتج معيب'),
        ('wrong_item', 'عنصر خاطئ'),
        ('not_as_described', 'لا يطابق الوصف'),
        ('damaged_shipping', 'تلف أثناء الشحن'),
        ('other', 'أخرى'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds', verbose_name="الدفعة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ الاسترداد")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name="سبب الاسترداد")
    description = models.TextField(blank=True, verbose_name="وصف الاسترداد")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="معرف معاملة الاسترداد")
    gateway_response = models.JSONField(blank=True, null=True, verbose_name="استجابة البوابة")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="تمت المعالجة بواسطة")
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ المعالجة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "استرداد"
        verbose_name_plural = "الاستردادات"
        ordering = ['-created_at']

    def __str__(self):
        return f"استرداد #{self.id} - {self.amount} ريال"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="الرصيد")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "محفظة"
        verbose_name_plural = "المحافظ"

    def __str__(self):
        return f"محفظة {self.user.username} - {self.balance} ريال"

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'إيداع'),
        ('debit', 'سحب'),
    ]

    TRANSACTION_REASONS = [
        ('refund', 'استرداد'),
        ('cashback', 'استرداد نقدي'),
        ('bonus', 'مكافأة'),
        ('purchase', 'شراء'),
        ('withdrawal', 'سحب'),
        ('adjustment', 'تعديل'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', verbose_name="المحفظة")
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="نوع المعاملة")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    reason = models.CharField(max_length=20, choices=TRANSACTION_REASONS, verbose_name="سبب المعاملة")
    description = models.TextField(blank=True, verbose_name="الوصف")
    reference_id = models.CharField(max_length=100, blank=True, verbose_name="المعرف المرجعي")
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الرصيد قبل المعاملة")
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الرصيد بعد المعاملة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "معاملة محفظة"
        verbose_name_plural = "معاملات المحافظ"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} ريال"

