
from .models import CompanyInformation


from django_tenants.utils import get_tenant

def company_info(request):
    # Check if the current schema is a tenant schema (not public)
    tenant = get_tenant(request)
    
    # Only run if we are in a tenant schema
    if tenant.schema_name != 'public':
        try:
            company = CompanyInformation.objects.first()
        except CompanyInformation.DoesNotExist:
            company = None
    else:
        company = None

    return {
        'company_info': company
    }

# def company_info(request):
#     try:
#         company = CompanyInformation.objects.first()
#     except CompanyInformation.DoesNotExist:
#         company = None

#     return {
#         'company_info': company
#     }
