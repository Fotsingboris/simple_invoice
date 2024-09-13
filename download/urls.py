from django.urls import path
from .views import *

app_name = "company"

urlpatterns = [
   path('company_info', CompanyInformationView.as_view(), name='company'),
    path('', home, name='home'),
    path('sale', create_invoice, name='sales'),
    path('all_sales', all_sale, name='all_sale'),
       path('download_pdf/<str:id>/', download_invoice_pdf, name='download_pdf'),

]