from django.urls import path
from .views import *

app_name = "company"

urlpatterns = [
   path('company_info', CompanyInformationView.as_view(), name='company_info'),
]