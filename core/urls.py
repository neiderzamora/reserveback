from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('reserve.urls')),
    path('user/', include('user.urls')),

    path('', TemplateView.as_view(template_name='index.html')),
    path('docs/', include_docs_urls(title='reserve API')),
]
