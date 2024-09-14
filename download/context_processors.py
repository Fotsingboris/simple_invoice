
from .models import CompanyInformation

def company_info(request):
    try:
        company = CompanyInformation.objects.first()
    except CompanyInformation.DoesNotExist:
        company = None

    return {
        'company_info': company
    }
