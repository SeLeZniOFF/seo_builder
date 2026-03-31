import re


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем хост (например, promo.site.com:8000 -> promo.site.com)
        host = request.get_host().split(':')[0]

        # Пропускаем запросы по голому IP или localhost
        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host) or host == 'localhost':
            request.subdomain = None
            return self.get_response(request)

        parts = host.split('.')
        request.subdomain = None

        # Если домен состоит из 3+ частей (promo.site.com) и это не www
        if len(parts) >= 3 and parts[0] != 'www':
            request.subdomain = parts[0]
        # Для локальных тестов (если настроишь site.localhost)
        elif len(parts) == 2 and parts[1] == 'localhost':
            request.subdomain = parts[0]

        return self.get_response(request)