# from django.db import models
import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django_extensions.db.models import TimeStampedModel, ActivatorModel

# Create your models here.

class BaseModel(TimeStampedModel, ActivatorModel):
    """
    Name: BaseModel

    Description: This class help to generate an uuid pk for all models means that all
                 the project's models should inherit from this model.

    Author: donaldtedom0@gmail.com
    """
    id = models.UUIDField(default=uuid.uuid4, null=False, blank=False, unique=True, primary_key=True)
    is_deleted = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, null=True, blank=True)
    #author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by')
    
class Client(BaseModel, TenantMixin):
    """ 
    Name: Client model.
    Description: This class help to create a client model.
    Author: donaldtedom0@gmail 
    
    """
    
   
    name = models.CharField(help_text="name of the client", max_length=100)
    
    organisation_code = models.CharField(max_length=128, unique=True, null=True, blank=True)

    on_trial = models.BooleanField("designate whether the user is on trial on not", default=True)
    
    created_on = models.DateField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    
    paid_until = models.DateField(default=None, null=True, blank=True)
    
    country = models.CharField(max_length=150, blank=True, null=True)
    
    city = models.CharField(max_length=150, blank=True, null=True)
    
    address_line1 = models.CharField(max_length=150, blank=True, null=True)
    
    address_line2 = models.CharField(max_length=150, blank=True, null=True)
    
    
    
    
    
    def __str__(self) -> str:
        return self.name
    
    
class Domain(DomainMixin):
    pass
