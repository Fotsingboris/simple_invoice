from django.shortcuts import render
from django.views import View
from django.conf import settings


site = settings.SITE

# Create your views here.
class HomeView(View):
    """  principal public view """
    def get(self, request, *args, **kwargs):
        return render(request, 'home/index.html', {'site': site})
    