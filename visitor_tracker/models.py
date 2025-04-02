from django.db import models

# VISITOR
class Visitor(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)   
    navigator_info = models.TextField(blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"user {self.id} use {self.navigator_info} on {self.os} device"

# VISIT INFO
class VisitInfo(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='visits')
    ip_address = models.GenericIPAddressField()
    location_approx = models.CharField(max_length=255, blank=True, null=True)
    visit_start_datetime = models.DateTimeField(auto_now_add=True)
    visit_end_datetime = models.DateTimeField(blank=True, null=True)
    visit_duration = models.DurationField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.ip_address} has visited for {self.visit_duration}"