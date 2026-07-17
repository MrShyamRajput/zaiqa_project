from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price = models.IntegerField()
    category = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'available': self.available,
            'image': self.image.url if self.image else None,
        }


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]
    table_number = models.CharField(max_length=50)
    items = models.JSONField()  # list of {name, quantity, price}
    total = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - Table {self.table_number}"

    def to_dict(self):
        return {
            'id': self.id,
            'table': self.table_number,
            'items': self.items,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }

class AISuggestion(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)