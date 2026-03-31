from django.contrib import admin
import nested_admin
from .models import Site, Page, BlockTemplate, PageBlock, Lead

# 1. Самый глубокий уровень: Блоки
class PageBlockInline(nested_admin.NestedTabularInline):
    model = PageBlock
    extra = 0 # Не плодить пустые строки по умолчанию
    sortable_field_name = "order" # Позволит менять порядок блоков перетаскиванием (drag-and-drop)

# 2. Средний уровень: Страницы (включает в себя Блоки)
class PageInline(nested_admin.NestedStackedInline):
    model = Page
    extra = 0
    inlines = [PageBlockInline] # Вкладываем блоки в страницы

# 3. Верхний уровень: Сайт (включает в себя Страницы)
@admin.register(Site)
class SiteAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'subdomain', 'language', 'created_at')
    search_fields = ('name', 'subdomain')
    inlines = [PageInline] # Вкладываем страницы в сайт

    # --- МАГИЯ: ПОДКЛЮЧАЕМ ИКОНКИ К АДМИНКЕ САЙТА ---
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',)
        }
        js = ('icon_picker.js',)

# Шаблоны блоков выводим отдельно, так как мы создаем их ДО создания сайтов
@admin.register(BlockTemplate)
class BlockTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'html_file')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('site', 'name', 'phone', 'created_at')
    list_filter = ('site', 'created_at') # Фильтры для аналитики
    readonly_fields = ('site', 'name', 'phone', 'email', 'created_at') # Чтобы случайно не изменить данные