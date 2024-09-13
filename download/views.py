import logging
from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.db import transaction
from .models import *
from django.contrib import messages



logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request, 'includes/main.html')


class CompanyInformationView(View):
    template_name = 'company/company.html'

    def get(self, request):
        company = CompanyInformation.objects.first()
        context = {
            'company': company
        }
        return render(request, self.template_name, context)

    def post(self, request):
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        action = request.POST.get('action')
        id = request.POST.get('id')

        if not action:
            messages.error(request, _('Action parameter is missing.'))
            return redirect('company:company')

        try:
            with transaction.atomic():
                if action == 'create':
                    company = CompanyInformation.objects.create(
                        name=name,
                        address=address,
                        phone_number=phone_number,
                        email=email,
                        image=image
                    )
                    messages.success(request, _('Company info created successfully'))
                    
                elif action == 'update':
                    company = CompanyInformation.objects.get(id=id)
                    company.name = name
                    company.email = email
                    company.phone_number = phone_number
                    company.address = address
                    if image:
                        company.image = image
                    company.save()
                    messages.success(request, _('Company info updated successfully'))
                
                elif action == 'delete':
                    company = CompanyInformation.objects.get(id=id)
                    company.delete()
                    messages.success(request, _('Company info deleted successfully'))
                    
                else:
                    messages.error(request, _('Invalid action'))
        
        except CompanyInformation.DoesNotExist:
            logger.error('CompanyInformation does not exist.')
            messages.error(request, _('Company Information not found.'))
        
        except transaction.TransactionManagementError as e:
            logger.error('TransactionManagementError occurred: %s', e)
            messages.error(request, _('Error handling transaction. Please contact support for assistance.'))
        
        except Exception as e:
            logger.error('Error occurred: %s', e)
            messages.error(request, _('Error adding Company Info. Please contact support for assistance.'))
        
        return redirect('company:company')
