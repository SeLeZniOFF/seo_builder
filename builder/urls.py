from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from builder import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('_nested_admin/', include('nested_admin.urls')),

    path('api/save-lead/', views.save_lead_api, name='save_lead_api'),

    # --- ТА САМАЯ ЗАГЛУШКА ДЛЯ КОРНЯ ---
    # Перехватывает http://127.0.0.1:8000/ и отдает пустую страницу
    path('', views.root_domain_view, name='root_domain_stub'),

    # Твои пути для сайтов (Лендинги):
    path('<str:subdomain>/sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('<str:subdomain>/', views.render_page, name='home_page'),
    path('<str:subdomain>/<slug:slug>/', views.render_page, name='inner_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)