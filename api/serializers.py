from rest_framework import serializers
from visitor_tracker.models import Visitor, VisitInfo


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id_visitor', 'navigator_info', 'os', 'device_type']

class VisitInfoSerializer(serializers.ModelSerializer):
    visitor = VisitorSerializer(read_only=True)
    class Meta:
        model = VisitInfo
        fields = '__all__'