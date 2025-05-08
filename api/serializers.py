from rest_framework import serializers
from .models import Product, Order, OrderItem

# Serializer for the Product model
class ProductSerializer(serializers.ModelSerializer):
    # This inner Meta class tells Django REST Framework which model to use
    # and which fields to include in the serialized output.
    class Meta:
        model = Product
        fields = (
            'id', 
            'description',      
            'name',     
            'price',    
            'stock',    
        )
    
    # Custom validator for the 'price' field
    def validate_price(self, value):
        """
        Validates that the price is greater than zero.
        Called automatically when data is serialized.
        """
        if value <= 0:
            raise serializers.ValidationError(
                'Product price must be greater than 0.'
            )
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    #product = ProductSerializer()

    # Instead of returning full product object, return specific fields from related product
    # 'source' is used to access related model fields
    product_name = serializers.CharField(source='product.name') 
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2
    )  

    class Meta:
        model = OrderItem
        fields = (
            'product_name',     
            'product_price',    
            'quantity',         
            'item_subtotal'     # Custom property from model (price * quantity)
        )

class OrderSerializer(serializers.ModelSerializer):
    # items is a reverse relation (Order → OrderItems)
    # many=True → One-to-many relationship (order has many order items)
    # read_only=True → Can't update this field through serializer
    items = OrderItemSerializer(many=True, read_only=True)

    # Adds a calculated field 'total_price' using a custom method
    total_price = serializers.SerializerMethodField(method_name='total')
    order_id = serializers.UUIDField(read_only=True)
    def total(self, obj):
        """
        Custom method to calculate total price of an order
        It sums all item_subtotals in the order
        """
        order_items = obj.items.all()

        return sum(order_item.item_subtotal for order_item in order_items)

    # Alternate version (Django convention) using get_<field_name> as method
    # total_price = serializers.SerializerMethodField()
    # def get_total_price(self, obj):
    # order_items = obj.items.all()
    # return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = (
            'order_id',     
            'created_at',   
            'user',         
            'status',       
            'items',        
            'total_price'   
        )


# A custom serializer (not model-based) for aggregated product info
class ProductInfoSerializer(serializers.Serializer):
    """
    Custom serializer to return summarized product info:
    - List of serialized products
    - Count of total products
    - Maximum price among products
    """

    products = ProductSerializer(many=True)  
    count = serializers.IntegerField()       
    max_price = serializers.FloatField()     

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product','quantity')

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True)

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data) #create parent object 

        for item in orderitem_data:
            OrderItem.objects.create(order=order,**item) #for individual child

        return order
    class Meta:
        model = Order
        fields = (
            'order_id',   
            'user',
            'status',
            'items',
        )
        extra_kwargs = {
            'user' :{'read_only': True}
        }