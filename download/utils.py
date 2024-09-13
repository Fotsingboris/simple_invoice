from download.models import Invoice


def generate_invoice_number():
    last_invoice = Invoice.objects.all().order_by('id').last()
    if not last_invoice:
        return 'INV0000001'
    
    invoice_number = last_invoice.invoice_number
    invoice_int = int(invoice_number.split('INV')[-1])
    new_invoice_int = invoice_int + 1
    new_invoice_number = 'INV' + str(new_invoice_int).zfill(7)  # Pad with leading zeros
    return new_invoice_number