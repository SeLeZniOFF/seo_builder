from django.template import Engine, Context
from django.template.loader import get_template
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Site, Page, Lead


def render_page(request, slug=''):
    # Ловим поддомен из нашего перехватчика (Middleware)
    subdomain = getattr(request, 'subdomain', None)

    # ТА САМАЯ ЗАГЛУШКА: Если зашли на главный домен (без поддомена) — отдаем 403
    if not subdomain:
        return HttpResponseForbidden("")

    site = get_object_or_404(Site, subdomain=subdomain)
    page = get_object_or_404(Page, site=site, slug=slug)
    page_blocks = page.blocks.all()

    # 1. Словарь перевода интерфейса
    ui_translations = {
        'ru': {'first_name': 'Имя', 'last_name': 'Фамилия', 'email': 'Почта', 'phone': 'Телефон',
               'send': 'Отправить заявку', 'rights': 'Все права защищены', 'form_title': 'Оставить заявку',
               'privacy': 'Политика конфиденциальности'},
        'en': {'first_name': 'First Name', 'last_name': 'Last Name', 'email': 'Email', 'phone': 'Phone',
               'send': 'Submit Request', 'rights': 'All rights reserved', 'form_title': 'Leave a request',
               'privacy': 'Privacy Policy'},
        'es': {'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo Electrónico', 'phone': 'Teléfono',
               'send': 'Regístrarse Ahora', 'rights': 'Todos los derechos reservados',
               'form_title': 'Crea tu cuenta gratis', 'privacy': 'Política de privacidad'},
        'de': {'first_name': 'Vorname', 'last_name': 'Nachname', 'email': 'E-Mail', 'phone': 'Telefon',
               'send': 'Konto erstellen', 'rights': 'Alle Rechte vorbehalten', 'form_title': 'Registrieren',
               'privacy': 'Datenschutzerklärung'},
    }
    lang = site.language.lower()
    ui = ui_translations.get(lang, ui_translations['en'])

    # 2. Обработка ГЕО
    GEO_MAPPING = {
        'gb': {'prefix': '+44', 'name': 'UK', 'length': 10}, 'es': {'prefix': '+34', 'name': 'España', 'length': 9},
        'it': {'prefix': '+39', 'name': 'Italia', 'length': 10}, 'fr': {'prefix': '+33', 'name': 'France', 'length': 9},
        'de': {'prefix': '+49', 'name': 'Deutschland', 'length': 11},
        'pl': {'prefix': '+48', 'name': 'Polska', 'length': 9},
        'pt': {'prefix': '+351', 'name': 'Portugal', 'length': 9},
        'nl': {'prefix': '+31', 'name': 'Netherlands', 'length': 9},
        'be': {'prefix': '+32', 'name': 'Belgium', 'length': 9},
        'ch': {'prefix': '+41', 'name': 'Switzerland', 'length': 9},
        'at': {'prefix': '+43', 'name': 'Austria', 'length': 10},
        'se': {'prefix': '+46', 'name': 'Sweden', 'length': 9},
        'no': {'prefix': '+47', 'name': 'Norway', 'length': 8}, 'dk': {'prefix': '+45', 'name': 'Denmark', 'length': 8},
        'fi': {'prefix': '+358', 'name': 'Finland', 'length': 10},
        'cz': {'prefix': '+420', 'name': 'Czechia', 'length': 9},
        'sk': {'prefix': '+421', 'name': 'Slovakia', 'length': 9},
        'hu': {'prefix': '+36', 'name': 'Hungary', 'length': 9},
        'ro': {'prefix': '+40', 'name': 'Romania', 'length': 9},
        'bg': {'prefix': '+359', 'name': 'Bulgaria', 'length': 9},
        'gr': {'prefix': '+30', 'name': 'Greece', 'length': 10},
        'rs': {'prefix': '+381', 'name': 'Serbia', 'length': 9},
        'hr': {'prefix': '+385', 'name': 'Croatia', 'length': 9},
        'si': {'prefix': '+386', 'name': 'Slovenia', 'length': 8},
        'lt': {'prefix': '+370', 'name': 'Lithuania', 'length': 8},
        'lv': {'prefix': '+371', 'name': 'Latvia', 'length': 8},
        'ee': {'prefix': '+372', 'name': 'Estonia', 'length': 8},
        'ie': {'prefix': '+353', 'name': 'Ireland', 'length': 9},
        'us': {'prefix': '+1', 'name': 'USA', 'length': 10}, 'ca': {'prefix': '+1', 'name': 'Canada', 'length': 10},
        'mx': {'prefix': '+52', 'name': 'México', 'length': 10},
        'br': {'prefix': '+55', 'name': 'Brasil', 'length': 11},
        'ar': {'prefix': '+54', 'name': 'Argentina', 'length': 10},
        'co': {'prefix': '+57', 'name': 'Colombia', 'length': 10},
        'cl': {'prefix': '+56', 'name': 'Chile', 'length': 9}, 'pe': {'prefix': '+51', 'name': 'Perú', 'length': 9},
        've': {'prefix': '+58', 'name': 'Venezuela', 'length': 7},
        'ec': {'prefix': '+593', 'name': 'Ecuador', 'length': 9},
        'gt': {'prefix': '+502', 'name': 'Guatemala', 'length': 8},
        'cr': {'prefix': '+506', 'name': 'Costa Rica', 'length': 8},
        'pa': {'prefix': '+507', 'name': 'Panamá', 'length': 8},
        'uy': {'prefix': '+598', 'name': 'Uruguay', 'length': 8},
        'py': {'prefix': '+595', 'name': 'Paraguay', 'length': 9},
        'bo': {'prefix': '+591', 'name': 'Bolivia', 'length': 8},
        'do': {'prefix': '+1', 'name': 'Dominican Rep.', 'length': 10},
        'sv': {'prefix': '+503', 'name': 'El Salvador', 'length': 8},
        'hn': {'prefix': '+504', 'name': 'Honduras', 'length': 8},
        'ni': {'prefix': '+505', 'name': 'Nicaragua', 'length': 8},
        'cn': {'prefix': '+86', 'name': 'China', 'length': 11}, 'in': {'prefix': '+91', 'name': 'India', 'length': 10},
        'jp': {'prefix': '+81', 'name': 'Japan', 'length': 10},
        'kr': {'prefix': '+82', 'name': 'South Korea', 'length': 10},
        'id': {'prefix': '+62', 'name': 'Indonesia', 'length': 11},
        'vn': {'prefix': '+84', 'name': 'Vietnam', 'length': 10},
        'th': {'prefix': '+66', 'name': 'Thailand', 'length': 9},
        'ph': {'prefix': '+63', 'name': 'Philippines', 'length': 10},
        'my': {'prefix': '+60', 'name': 'Malaysia', 'length': 10},
        'sg': {'prefix': '+65', 'name': 'Singapore', 'length': 8},
        'pk': {'prefix': '+92', 'name': 'Pakistan', 'length': 10},
        'bd': {'prefix': '+880', 'name': 'Bangladesh', 'length': 10},
        'au': {'prefix': '+61', 'name': 'Australia', 'length': 9},
        'nz': {'prefix': '+64', 'name': 'New Zealand', 'length': 9},
        'tr': {'prefix': '+90', 'name': 'Turkey', 'length': 10}, 'ae': {'prefix': '+971', 'name': 'UAE', 'length': 9},
        'sa': {'prefix': '+966', 'name': 'Saudi Arabia', 'length': 9},
        'il': {'prefix': '+972', 'name': 'Israel', 'length': 9},
        'eg': {'prefix': '+20', 'name': 'Egypt', 'length': 10},
        'za': {'prefix': '+27', 'name': 'South Africa', 'length': 9},
        'ng': {'prefix': '+234', 'name': 'Nigeria', 'length': 10},
        'ke': {'prefix': '+254', 'name': 'Kenya', 'length': 9},
        'ma': {'prefix': '+212', 'name': 'Morocco', 'length': 9},
        'dz': {'prefix': '+213', 'name': 'Algeria', 'length': 9},
        'qa': {'prefix': '+974', 'name': 'Qatar', 'length': 8}, 'kw': {'prefix': '+965', 'name': 'Kuwait', 'length': 8},
    }

    raw_geos = [g.strip().lower() for g in site.allowed_geos.split(',') if g.strip()]
    site_geos = []
    for g in raw_geos:
        if g in GEO_MAPPING:
            site_geos.append(GEO_MAPPING[g])
        else:
            site_geos.append({'prefix': '', 'name': g.upper(), 'length': 15})

    if not site_geos:
        site_geos = [{'prefix': '+1', 'name': 'USA', 'length': 10}]

    engine = Engine.get_default()

    header_html = ""
    if site.header_template and site.header_template.html_code:
        h_str = json.dumps(site.header_json or {}, ensure_ascii=False).replace('[site_name]', site.name)
        h_ctx = Context({'site': site, 'page': page, 'content': json.loads(h_str), 'ui': ui, 'site_geos': site_geos})
        header_html = engine.from_string(site.header_template.html_code).render(h_ctx)

    footer_html = ""
    if site.footer_template and site.footer_template.html_code:
        f_str = json.dumps(site.footer_json or {}, ensure_ascii=False).replace('[site_name]', site.name)
        f_ctx = Context({'site': site, 'page': page, 'content': json.loads(f_str), 'ui': ui, 'site_geos': site_geos})
        footer_html = engine.from_string(site.footer_template.html_code).render(f_ctx)

    blocks_with_data = []

    for block in page_blocks:
        content_data = block.content_json if block.content_json else {}
        content_str = json.dumps(content_data, ensure_ascii=False)
        content_str = content_str.replace('Feralyx AI', site.name).replace('Feralyx', site.name)
        content_str = content_str.replace('NeralyxAI', site.name).replace('Neralyx', site.name)
        content_str = content_str.replace('[site_name]', site.name)
        clean_content = json.loads(content_str)

        block_context = Context({
            'site': site,
            'page': page,
            'content': clean_content,
            'content_image': block.image,
            'image_pos': block.image_position,
            'ui': ui,
            'site_geos': site_geos,
        })

        rendered_html = ""
        if block.block_template.html_code:
            template_obj = engine.from_string(block.block_template.html_code)
            rendered_html = template_obj.render(block_context)
        elif block.block_template.html_file:
            template_obj = get_template(block.block_template.html_file)
            rendered_html = template_obj.render(block_context.flatten())

        blocks_with_data.append(rendered_html)

    context = {
        'site': site,
        'page': page,
        'blocks': blocks_with_data,
        'ui': ui,
        'site_geos': site_geos,
        'header_html': header_html,
        'footer_html': footer_html,
    }
    return render(request, 'base.html', context)


@csrf_exempt
def save_lead_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Поддомен приходит из JS-скрипта (мы его не трогали, он работает отлично)
            subdomain = data.get('subdomain')

            site = Site.objects.filter(subdomain=subdomain).first()
            if site:
                first_name = data.get('firstName', '')
                last_name = data.get('lastName', '')
                full_name = f"{first_name} {last_name}".strip()

                Lead.objects.create(
                    site=site,
                    name=full_name,
                    phone=data.get('phone', ''),
                    email=data.get('email', '')
                )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "bad request"}, status=400)


def sitemap_xml(request):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return HttpResponseForbidden("")

    site = get_object_or_404(Site, subdomain=subdomain)
    pages = site.pages.all()

    # Теперь мы генерируем правильные ссылки для реальных поддоменов
    base_url = f"{request.scheme}://{request.get_host()}"

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for page in pages:
        if page.slug:
            page_url = f"{base_url}/{page.slug}/"
            priority = "0.8"
        else:
            page_url = f"{base_url}/"
            priority = "1.0"

        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{page_url}</loc>')
        xml_lines.append('    <changefreq>daily</changefreq>')
        xml_lines.append(f'    <priority>{priority}</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    return HttpResponse('\n'.join(xml_lines), content_type='application/xml')


def robots_txt(request):
    subdomain = getattr(request, 'subdomain', None)
    if not subdomain:
        return HttpResponseForbidden("")

    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def thanks_page(request):
    subdomain = getattr(request, 'subdomain', None)

    # Если зашли на главный домен (без поддомена) — отдаем 403
    if not subdomain:
        return HttpResponseForbidden("")

    site = get_object_or_404(Site, subdomain=subdomain)

    # Отдаем универсальный шаблон, но передаем в него данные ТЕКУЩЕГО сайта
    return render(request, 'thanks.html', {'site': site})