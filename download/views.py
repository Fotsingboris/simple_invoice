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
        
        try:
            with transaction.atomic():
                if action == 'create':
                    company = CompanyInformation.objects.create(
                        name=name,
                        address=address,
                        phone_number=phone_number,
                        email=email,
                        image = image
                    )
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
        except transaction.TransactionManagementError as e:
            logger.error('TransactionManagementError occurred: %s', e)
            messages.error(request, _('Error adding Company Info. Please contact support for assistance.'))
        except Exception as e:
            logger.error('Error adding Company Info: %s', e)
            messages.error(request, _('Error adding Company Info. Please contact support for assistance.'))
        return redirect('company:company')