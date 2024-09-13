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
