import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model inheriting from Django's built-in AbstractUser
class User(AbstractUser):
    pass


# Product model to represent items in the store
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    stock = models.PositiveIntegerField() 
    image = models.ImageField(upload_to='products/', blank=True, null=True)  

    @property
    def in_stock(self):
        # Returns True if the stock is more than 0
        return self.stock > 0
    
    def __str__(self):
        # String representation of the product (for admin and shell)
        return self.name


# Order model to store order details
class Order(models.Model):
    # Choices for order status
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        CANCELLED = 'Cancelled'

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # Unique ID for the order
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who placed the order
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the order was created
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,  # Dropdown of status options
        default=StatusChoices.PENDING   # Default status is 'Pending'
    )

    products = models.ManyToManyField(
        Product,
        through="OrderItem",  # Intermediate model for storing quantity
        related_name='orders'
    )

    def __str__(self):
        # String representation of the order
        return f"Order {self.order_id} by {self.user.username}"


# Intermediate model to link Orders and Products with quantity
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Belongs to one order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Refers to one product
    quantity = models.PositiveIntegerField()  # Quantity of that product in the order

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"
