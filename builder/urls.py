from django.urls import path
from builder import views

urlpatterns = [
    # API и системные файлы
    path('api/save-lead/', views.save_lead_api, name='save_lead_api'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # Твои пути для страниц (Лендинги):
    # Порядок ВАЖЕН: сначала пути со slug, потом пустой путь
    path('<slug:slug>/', views.render_page, name='inner_page'),
    path('', views.render_page, name='home_page'),
]