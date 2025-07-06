from django.db import models

# VISITOR
class Visitor(models.Model):
    id_visitor = models.UUIDField(primary_key=True, editable=False)   
    navigator_info = models.TextField(blank=True, null=True)
    os = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    is_new_visitor = models.BooleanField(default=True)

    def __str__(self):
        return f"user {self.id_visitor} use {self.navigator_info} on {self.os} device"

# VISIT INFO
class VisitInfo(models.Model):
    id_visit_info = models.UUIDField(primary_key=True, editable=False) 
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
    
# CV DOWNLOAD
class CVDownload(models.Model):
    id_cv_download = models.UUIDField(primary_key=True, editable=False)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='cv_downloads')
    download_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"downloaded by {self.visitor}"

# PORTFOLIO DETAIL VIEW
class PortfolioDetailView(models.Model):
    id_portfolio_detail_view = models.UUIDField(primary_key=True, editable=False)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='portfolio_detail_view')
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_type = models.CharField(max_length=255, blank=True, null=True)
    view_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Portfolio detail viewed by {self.visitor}"

# WOOSEEANDY USER/TOKEN
class PushToken(models.Model):
    user_id = models.CharField(max_length=100)  # ou models.ForeignKey(User) si t'as un système de login
    expo_push_token = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_id} - {self.expo_push_token}'