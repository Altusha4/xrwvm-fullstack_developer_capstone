from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from djangoapp.views import frontend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),
    path('', TemplateView.as_view(template_name='Home.html')),
    path('about/', TemplateView.as_view(template_name='About.html')),
    path('contact/', TemplateView.as_view(template_name='Contact.html')),
    path('login', frontend), path('register', frontend),
    path('dealers', frontend), path('dealer/<int:id>', frontend),
    path('postreview/<int:id>', frontend),
]
