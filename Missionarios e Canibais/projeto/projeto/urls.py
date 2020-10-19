from django.contrib import admin
from django.urls import path, include
import app.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='url_home'),
    path('tabela_solucao', views.tabela_solucao, name='url_tabela_solucao'),
    path('conclusao', views.conclusao, name='url_conclusao'),
]