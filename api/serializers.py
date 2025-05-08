from rest_framework import serializers
from visitor_tracker.models import Visitor, VisitInfo, CVDownload, PortfolioDetailView


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id_visitor', 'navigator_info', 'os', 'device_type', 'is_new_visitor']

class VisitInfoSerializer(serializers.ModelSerializer):
    visitor = VisitorSerializer(read_only=True)
    class Meta:
        model = VisitInfo
        fields = '__all__'

class CVDownloadSerializer(serializers.ModelSerializer):
    visitor = VisitorSerializer(read_only=True)
    class Meta:
        model = CVDownload
        fields = '__all__'

class PortfolioDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioDetailView
        fields = '__all__'