from datetime import date
import logging
import pdfkit

from django.shortcuts import get_object_or_404, render
from django.views import View
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.db import transaction
from django.template.loader import get_template
from .utils import generate_invoice_number
from .models import *
from django.contrib import messages
from datetime import date
from django.http import HttpResponse




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


def all_sale(request):
    invoices = Invoice.objects.select_related().prefetch_related('items').all()

    context = {
        'invoices': invoices,
    }
    return render(request, 'Sales/all_sales.html', context)



def create_invoice(request):
    if request.method == 'POST':
        # Create the invoice
        invoice_number = request.POST.get('invoice_number')
        invoice_date = request.POST.get('date')
        
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            date=invoice_date,
        )
        
        # Save each product row as an InvoiceItem
        product_names = request.POST.getlist('product_name[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        for product_name, quantity, unit_price in zip(product_names, quantities, unit_prices):
            InvoiceItem.objects.create(
                invoice=invoice,
                product_name=product_name,
                quantity=int(quantity),
                unit_price=float(unit_price),
            )

        return redirect('company:sales')

    # For GET request, generate an invoice number and load form
    invoice_number = generate_invoice_number()
    today_date = date.today()

    return render(request, 'Sales/sales.html', {
        'invoice_number': invoice_number,
        'date': today_date,
    })


def download_invoice_pdf(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    invoice_items = invoice.items.all()

    # Calculate the total amount
    total_amount = sum(item.total_price for item in invoice_items)

    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'total_amount': total_amount,
        'current_date': date.today().strftime('%d/%m/%Y'),
    }

    template = get_template('Sales/invoice_pdf.html')
    html = template.render(context)
    pdf = pdfkit.from_string(html, False)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    return response
