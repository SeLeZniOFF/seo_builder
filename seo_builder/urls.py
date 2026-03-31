from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Глобальная админка
    path('admin/', admin.site.urls),
    path('_nested_admin/', include('nested_admin.urls')),

    # Все остальные запросы (сайт, апи, лендинги) отправляем в приложение builder
    path('', include('builder.urls')),
]

# МАГИЯ КАРТИНОК: Разрешаем Django отдавать медиа-файлы в браузере (только для режима DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)