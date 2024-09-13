from django.db import models

# Create your models here.

class CompanyInformation(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to='media/company', null=True, blank=True)
    
    def __str__(self):
        return self.name


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField(auto_now_add=True)
    
    @property
    def total_amount(self):
        # Sum up all the item prices to get the total invoice amount
        return sum(item.total_price for item in self.items.all())
    
    def __str__(self):
        return f'Invoice {self.invoice_number}'


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price  # Calculate total price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product_name} (x{self.quantity})'
