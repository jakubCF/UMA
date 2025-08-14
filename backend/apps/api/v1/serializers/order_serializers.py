from rest_framework import serializers
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = '__all__'

    def update(self, instance, validated_data):
        # 1. First, extract the nested 'items' data from the validated_data
        #    We use .pop() to remove it so that super().update() doesn't try to
        #    update it directly, which would cause an error.
        items_validated_data = validated_data.pop('items', None)

        # 2. Get the original nested item data from the initial_data
        #    This is where the 'id's are present
        items_initial_data = self.initial_data.get('items', None)

        # 3. Update the parent Order instance first
        instance = super().update(instance, validated_data)

        # 4. If there is nested item data, iterate through it and update each item
        if items_validated_data is not None and items_initial_data is not None:
            # We use zip to pair the id from the initial data with the validated data
            for item_initial, item_validated in zip(items_initial_data, items_validated_data):
                item_id = item_initial.get('id')
                if item_id and instance.items.filter(id=item_id).exists():
                    item_instance = instance.items.get(id=item_id)
                    # Use the OrderItemSerializer to validate and update the item
                    item_serializer = OrderItemSerializer(item_instance, data=item_validated, partial=True)
                    if item_serializer.is_valid(raise_exception=True):
                        item_serializer.save()

        # 5. Return the updated parent instance
        return instance