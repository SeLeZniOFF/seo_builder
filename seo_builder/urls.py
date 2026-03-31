from django.contrib import admin
from django.urls import path, include # Добавили include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('_nested_admin/', include('nested_admin.urls')), # Служебная ссылка для админки
    path('', include('builder.urls')), # Все остальные запросы отправляем в наше приложение
]