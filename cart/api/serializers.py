from rest_framework import serializers

class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)

class UpdateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=0)

class RemoveItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.CharField(allow_null=True)
    qty = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)

class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_qty = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
