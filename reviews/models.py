from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews', verbose_name="المنتج")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, blank=True, null=True, verbose_name="عنصر الطلب")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="التقييم"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان المراجعة")
    comment = models.TextField(verbose_name="التعليق")
    is_verified_purchase = models.BooleanField(default=False, verbose_name="شراء محقق")
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")
    helpful_count = models.PositiveIntegerField(default=0, verbose_name="عدد الإعجابات")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مراجعة"
        verbose_name_plural = "المراجعات"
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating}/5)"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images', verbose_name="المراجعة")
    image = models.ImageField(upload_to='reviews/', verbose_name="الصورة")
    caption = models.CharField(max_length=200, blank=True, verbose_name="التسمية التوضيحية")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة مراجعة"
        verbose_name_plural = "صور المراجعات"

    def __str__(self):
        return f"صورة لمراجعة {self.review.product.name}"

class ReviewHelpful(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes', verbose_name="المراجعة")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    is_helpful = models.BooleanField(verbose_name="مفيد")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تصويت مفيد"
        verbose_name_plural = "تصويتات مفيدة"
        unique_together = ['review', 'user']

    def __str__(self):
        return f"{self.user.username} - {'مفيد' if self.is_helpful else 'غير مفيد'}"

class Question(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='questions', verbose_name="المنتج")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    question = models.TextField(verbose_name="السؤال")
    is_answered = models.BooleanField(default=False, verbose_name="تم الإجابة")
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"
        ordering = ['-created_at']

    def __str__(self):
        return f"سؤال حول {self.product.name}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="السؤال")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    answer = models.TextField(verbose_name="الإجابة")
    is_seller = models.BooleanField(default=False, verbose_name="من البائع")
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")
    helpful_count = models.PositiveIntegerField(default=0, verbose_name="عدد الإعجابات")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "إجابة"
        verbose_name_plural = "الإجابات"
        ordering = ['-is_seller', '-helpful_count', '-created_at']

    def __str__(self):
        return f"إجابة على سؤال حول {self.question.product.name}"

