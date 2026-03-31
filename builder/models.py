from deep_translator import GoogleTranslator
from django.db import models


class Site(models.Model):
    # Добавим список доступных шрифтов
    FONT_CHOICES = [
        ('Inter', 'Inter (Современный, чистый)'),
        ('Montserrat', 'Montserrat (Геометричный, стильный)'),
        ('Roboto', 'Roboto (Классический)'),
        ('Playfair Display', 'Playfair (Премиальный, с засечками)'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название проекта")
    subdomain = models.CharField(max_length=100, unique=True, verbose_name="Поддомен")
    language = models.CharField(max_length=10, default='en', verbose_name="Язык сайта")

    allowed_geos = models.CharField(max_length=200, default="ru", verbose_name="Разрешенные ГЕО")

    header_template = models.ForeignKey('BlockTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="Шаблон Шапки")
    header_json = models.JSONField(blank=True, null=True, verbose_name="Контент шапки (JSON)")

    footer_template = models.ForeignKey('BlockTemplate', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name="Шаблон Футера")
    footer_json = models.JSONField(blank=True, null=True, verbose_name="Контент футера (JSON)")

    # --- НОВЫЕ ПОЛЯ ДЛЯ ДИЗАЙНА ---
    logo_text = models.CharField(max_length=50, blank=True, verbose_name="Текст логотипа",
                                 help_text="Оставьте пустым, чтобы использовать название проекта")
    font_family = models.CharField(max_length=50, choices=FONT_CHOICES, default='Inter', verbose_name="Шрифт сайта")
    rounded_corners = models.BooleanField(default=True, verbose_name="Скругленные углы дизайна")
    # ------------------------------

    color_main = models.CharField(max_length=20, default="#000000", verbose_name="Основной цвет")
    color_accent = models.CharField(max_length=20, default="#FFFFFF", verbose_name="Акцентный цвет")
    gsc_code = models.TextField(blank=True, verbose_name="Код Google Search Console")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сайт"
        verbose_name_plural = "Сайты"

    def save(self, *args, **kwargs):
        # Автоперевод Шапки
        if not self.header_json and self.header_template and self.header_template.default_content:
            target_lang = self.language.lower()
            if target_lang == 'ru':
                self.header_json = self.header_template.default_content
            else:
                try:
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    self.header_json = {k: translator.translate(v) if isinstance(v, str) else v for k, v in
                                        self.header_template.default_content.items()}
                except Exception:
                    self.header_json = self.header_template.default_content

        # Автоперевод Футера
        if not self.footer_json and self.footer_template and self.footer_template.default_content:
            target_lang = self.language.lower()
            if target_lang == 'ru':
                self.footer_json = self.footer_template.default_content
            else:
                try:
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    self.footer_json = {k: translator.translate(v) if isinstance(v, str) else v for k, v in
                                        self.footer_template.default_content.items()}
                except Exception:
                    self.footer_json = self.footer_template.default_content

        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.name} ({self.subdomain})"


class Page(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pages', verbose_name="Сайт")
    title = models.CharField(max_length=200, verbose_name="Название страницы (Title)")
    slug = models.SlugField(verbose_name="URL страницы (пусто = главная)", blank=True)

    icon_class = models.CharField(
        max_length=50,
        default='bi-file-earmark-text',
        verbose_name="Иконка (Bootstrap Icon)",
        help_text="Например: bi-house (Главная), bi-envelope (Контакты), bi-info-circle (О нас). Ищи на icons.getbootstrap.com"
    )
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Meta Title",
                                  help_text="Если пусто, возьмется название страницы + название сайта")
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    og_image = models.CharField(max_length=500, blank=True, verbose_name="Ссылка на картинку (OpenGraph)",
                                help_text="Вставьте URL картинки для превью в соцсетях/мессенджерах")

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        unique_together = ('site', 'slug')  # Защита от дублей страниц на одном сайте

    def __str__(self):
        return f"{self.site.subdomain} -> {self.title}"


class BlockTemplate(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блока (для админки)")
    html_file = models.CharField(max_length=200, blank=True, null=True, verbose_name="Путь к HTML (Устарело)")
    html_code = models.TextField(blank=True, null=True, verbose_name="HTML код блока", help_text="Вставьте HTML код прямо сюда. Поддерживаются теги Django.")
    # ПОЛЕ ДЛЯ БАЗОВОГО ТЕКСТА (который мы будем переводить)
    default_content = models.JSONField(
        blank=True, null=True,
        verbose_name="Стандартный контент (JSON)",
        help_text="Базовый текст на русском. Будет переведен автоматически."
    )

    class Meta:
        verbose_name = "Шаблон блока"
        verbose_name_plural = "Шаблоны блоков"

    def __str__(self):
        return self.name


class PageBlock(models.Model):
    IMAGE_POSITION_CHOICES = [
        ('right', 'Картинка справа (на мобильном снизу)'),
        ('left', 'Картинка слева (на мобильном сверху)'),
        ('top', 'Картинка сверху (по центру)'),
        ('background', 'Картинка на фоне (с авто-затемнением)'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='blocks', verbose_name="Страница")
    block_template = models.ForeignKey(BlockTemplate, on_delete=models.CASCADE, verbose_name="Шаблон блока")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок вывода (0, 1, 2...)")
    content_json = models.JSONField(blank=True, null=True, verbose_name="Контент (тексты, картинки)")

    # --- ДОБАВЛЕННЫЕ ПОЛЯ ДЛЯ КАРТИНКИ И ЕЕ ПОЗИЦИИ ---
    image = models.ImageField(upload_to='block_images/', blank=True, null=True, verbose_name="Изображение блока")
    image_position = models.CharField(
        max_length=20,
        choices=IMAGE_POSITION_CHOICES,
        default='right',
        verbose_name="Расположение картинки"
    )

    # --------------------------------------------------

    class Meta:
        ordering = ['order']
        verbose_name = "Блок на странице"
        verbose_name_plural = "Блоки на странице"

    # --- МАГИЯ АВТОПЕРЕВОДА ---
    def save(self, *args, **kwargs):
        # Проверяем: если контент не заполнен вручную, но есть базовый текст в шаблоне
        if not self.content_json and self.block_template.default_content:
            base_content = self.block_template.default_content

            # Узнаем целевой язык из настроек сайта
            target_lang = self.page.site.language.lower()

            # Если язык русский (исходный), то просто копируем без перевода
            if target_lang == 'ru':
                self.content_json = base_content
            else:
                translated_content = {}
                try:
                    # Инициализируем переводчик (с автоопределения на нужный язык)
                    translator = GoogleTranslator(source='auto', target=target_lang)

                    # Перебираем все ключи в JSON
                    for key, value in base_content.items():
                        if isinstance(value, str):
                            # Переводим только текстовые значения
                            translated_content[key] = translator.translate(value)
                        else:
                            # Числа, списки или вложенные словари оставляем как есть
                            translated_content[key] = value

                    self.content_json = translated_content
                except Exception as e:
                    print(f"Ошибка перевода: {e}")
                    # Если API Гугла отвалилось, сохраняем хотя бы оригинальный текст, чтобы сайт не сломался
                    self.content_json = base_content

        # Сохраняем объект в базу
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Блок {self.block_template.name} на {self.page.title}"


class Lead(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='leads', verbose_name="Сайт")
    name = models.CharField(max_length=150, verbose_name="Имя", blank=True)
    phone = models.CharField(max_length=50, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка с {self.site.subdomain} - {self.phone}"