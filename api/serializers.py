from rest_framework import serializers
from visitor_tracker.models import Visitor

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'navigator_info', 'os', 'device_type']
