from datetime import date
import logging
import pdfkit
from weasyprint import HTML


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
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta




logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Weekly Sales
    weekly_sales = Invoice.objects.filter(date__range=[start_of_week, end_of_week]).aggregate(total_sales=Sum('total_price'))['total_sales'] or 0

    # Weekly Orders
    weekly_orders = Invoice.objects.filter(date__range=[start_of_week, end_of_week]).count()

    # Day with Best Sale
    sales_per_day = Invoice.objects.filter(date__range=[start_of_week, end_of_week]) \
        .values('created') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('-total_sales')
    
    if sales_per_day:
        best_day = sales_per_day[0]
        best_day_date = best_day['created']
        best_day_sales = best_day['total_sales']
    else:
        best_day_date = None
        best_day_sales = 0
    
    # Sales per Month
    current_year = today.year
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_sales = Invoice.objects.filter(date__year=current_year) \
        .values('date__month') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('date__month')

    monthly_sales_data = [0] * 12
    for entry in monthly_sales:
        month_index = entry['date__month'] - 1
        monthly_sales_data[month_index] = entry['total_sales']

    # Sales per Weekday
    sales_per_weekday = Invoice.objects.filter(date__range=[start_of_week, end_of_week]) \
        .values('created') \
        .annotate(total_sales=Sum('total_price')) \
        .order_by('created')

    weekly_sales_data = [0] * 7
    for sale in sales_per_weekday:
        weekday = sale['created'].weekday()
        weekly_sales_data[weekday] += sale['total_sales']

    weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


    context = {
        'weekly_sales': weekly_sales,
        'weekly_orders': weekly_orders,
        'best_day_date': best_day_date,
        'best_day_sales': best_day_sales,
        'monthly_sales_data': monthly_sales_data,
        'weekly_sales_data': weekly_sales_data,
        'month_names': month_names,
        'weekday_labels': weekday_labels,
    }

    return render(request, 'includes/main.html', context)


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
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        date = request.POST.get('date')
        # invoice_date = request.POST.get('date')

        # Save each product row as an InvoiceItem
        product_names = request.POST.getlist('product_name[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        # Create the invoice first, with initial total_price and total_quantity as placeholders
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            date=date,
            total_price=0,  # to be updated later
            total_quantity=0  # to be updated later
        )

        total_price = 0
        distinct_products = set()  # To keep track of unique products

        for product_name, quantity, unit_price in zip(product_names, quantities, unit_prices):
            quantity = int(quantity)
            unit_price = float(unit_price)
            total_price += quantity * unit_price  # Sum total price for the invoice
            
            # Save each product as an InvoiceItem
            InvoiceItem.objects.create(
                invoice_id=invoice,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price
            )

            # Add product name to distinct_products to calculate total_quantity
            distinct_products.add(product_name)

        # Update the invoice with the final total_price and total_quantity
        invoice.total_price = total_price
        invoice.total_quantity = len(distinct_products)
        invoice.save()
        messages.success(request, _('Invoice created successfully'))
        

        return redirect('company:sales')

    # For GET request, generate an invoice number and load form
    # invoice_number = generate_invoice_number()
    # today_date = date.today()

    return render(request, 'Sales/sales.html', {
        # 'invoice_number': invoice_number,
        # 'date': today_date,
    })


def download_invoice_pdf(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    invoice_items = invoice.items.all()
    company = CompanyInformation.objects.first()    

    # Calculate the total amount
    total_amount = sum(item.total_price for item in invoice_items)

    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'total_amount': total_amount,
        'company': company,
        'current_date': date.today().strftime('%d/%m/%Y'),
    }

    template = get_template('Sales/invoice_pdf.html')
    # html = template.render(context)
    # pdf = pdfkit.from_string(html, False)
    html_content = template.render(context)
    
    # Generate the PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    return response



def update_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == 'POST':
        # Update the invoice details
        invoice.invoice_number = request.POST.get('invoice_number')
        invoice.client_name = request.POST.get('client_name')
        invoice.client_email = request.POST.get('client_email')
        invoice.client_phone = request.POST.get('client_phone')
        invoice.date = request.POST.get('date')

        # Remove the old invoice items and replace them with new ones
        InvoiceItem.objects.filter(invoice_id=invoice).delete()

        # Save updated product rows as new InvoiceItems
        product_names = request.POST.getlist('product_name[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        total_price = 0
        distinct_products = set()  # To keep track of unique products

        for product_name, quantity, unit_price in zip(product_names, quantities, unit_prices):
            quantity = int(quantity)
            unit_price = float(unit_price)
            total_price += quantity * unit_price  # Sum total price for the invoice

            # Save each product as an InvoiceItem
            InvoiceItem.objects.create(
                invoice_id=invoice,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price
            )

            # Add product name to distinct_products to calculate total_quantity
            distinct_products.add(product_name)

        # Update the invoice with the final total_price and total_quantity
        invoice.total_price = total_price
        invoice.total_quantity = len(distinct_products)
        invoice.save()

        messages.success(request, _('Invoice updated successfully'))

        return redirect('company:sales')

    return render(request, 'Sales/update_invoice.html', {
        'invoice': invoice,
        'invoice_items': invoice.items.all(),  # Pass the related invoice items
    })


def reuse_invoice(request, invoice_id):
    original_invoice = get_object_or_404(Invoice, id=invoice_id)
    original_items = InvoiceItem.objects.filter(invoice_id=original_invoice)

    if request.method == 'POST':
        # Create the new invoice
        new_invoice_number = generate_invoice_number()  # Ensure to implement this function
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        invoice_date = request.POST.get('date')

        # Save the new invoice
        new_invoice = Invoice.objects.create(
            invoice_number=new_invoice_number,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            date=invoice_date,
            total_price=0,  # to be updated later
            total_quantity=0  # to be updated later
        )

        total_price = 0
        distinct_products = set()  # To keep track of unique products

        # Save each product row as an InvoiceItem for the new invoice
        for item in original_items:
            quantity = item.quantity
            unit_price = item.unit_price
            total_price += quantity * unit_price  # Sum total price for the invoice
            
            # Create a new InvoiceItem for the new invoice
            InvoiceItem.objects.create(
                invoice_id=new_invoice,
                product_name=item.product_name,
                quantity=quantity,
                unit_price=unit_price
            )

            # Add product name to distinct_products to calculate total_quantity
            distinct_products.add(item.product_name)

        # Update the new invoice with the final total_price and total_quantity
        new_invoice.total_price = total_price
        new_invoice.total_quantity = len(distinct_products)
        new_invoice.save()

        messages.success(request, 'Invoice reused and created successfully')
        return redirect('company:sales')

    return render(request, 'Sales/resuse_sale.html', {
        'invoice': original_invoice,
        'invoice_items': original_items,
        # 'date': date.today()
    })
