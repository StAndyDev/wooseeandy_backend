from rest_framework import serializers
from visitor_tracker.models import Visitor, VisitInfo

class VisitInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitInfo
        fields = '__all__'

class VisitorSerializer(serializers.ModelSerializer):
    visit_info = VisitInfoSerializer(source='visits', many=True)
    class Meta:
        model = Visitor
        fields = ['id', 'navigator_info', 'os', 'device_type', 'visit_info']