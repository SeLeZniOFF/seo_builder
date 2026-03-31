document.addEventListener("DOMContentLoaded", function() {
    // База популярных иконок
    const icons = [
        'bi-house-fill', 'bi-info-circle-fill', 'bi-envelope-fill', 'bi-telephone-fill',
        'bi-person-fill', 'bi-cart-fill', 'bi-gear-fill', 'bi-star-fill', 'bi-heart-fill',
        'bi-chat-dots-fill', 'bi-box-seam-fill', 'bi-briefcase-fill', 'bi-calendar-event-fill',
        'bi-camera-fill', 'bi-compass-fill', 'bi-credit-card-fill', 'bi-geo-alt-fill',
        'bi-globe', 'bi-image-fill', 'bi-lightning-fill', 'bi-lock-fill', 'bi-map-fill',
        'bi-megaphone-fill', 'bi-palette-fill', 'bi-pen-fill', 'bi-pie-chart-fill',
        'bi-pin-map-fill', 'bi-play-circle-fill', 'bi-question-circle-fill', 'bi-search',
        'bi-shield-check', 'bi-shop', 'bi-tag-fill', 'bi-truck', 'bi-wallet-fill', 'bi-wrench'
    ];

    // Функция, которая превращает обычное текстовое поле в красивую галерею
    function initIconPicker(inputField) {
        if (inputField.dataset.pickerInitialized) return; // Защита от двойной отрисовки
        inputField.dataset.pickerInitialized = "true";

        const preview = document.createElement("div");
        preview.style.margin = "10px 0";
        preview.innerHTML = `<span style="font-weight:bold; color:#444;">Текущая иконка:</span> <i class="bi ${inputField.value}" style="font-size: 28px; margin-left: 10px; color: #417690; vertical-align: middle;"></i>`;

        const container = document.createElement("div");
        container.style.marginTop = "10px";
        container.style.padding = "15px";
        container.style.border = "1px solid #ccc";
        container.style.borderRadius = "8px";
        container.style.background = "#f8f8f8";
        container.style.maxWidth = "450px";
        container.style.display = "flex";
        container.style.flexWrap = "wrap";
        container.style.gap = "12px";

        inputField.parentNode.insertBefore(preview, inputField.nextSibling);
        inputField.parentNode.insertBefore(container, preview.nextSibling);
        inputField.style.opacity = "0.5";

        icons.forEach(iconClass => {
            const btn = document.createElement("div");
            btn.className = `bi ${iconClass}`;
            btn.style.fontSize = "26px";
            btn.style.cursor = "pointer";
            btn.style.padding = "8px";
            btn.style.border = "2px solid transparent";
            btn.style.borderRadius = "8px";
            btn.style.color = "#555";
            btn.style.transition = "0.2s";
            btn.title = iconClass;

            if (inputField.value === iconClass) {
                btn.style.border = "2px solid #417690";
                btn.style.background = "#e1eef4";
                btn.style.color = "#417690";
            }

            btn.onmouseover = () => { if (inputField.value !== iconClass) btn.style.transform = "scale(1.2)"; };
            btn.onmouseout = () => { btn.style.transform = "scale(1)"; };

            btn.addEventListener("click", () => {
                inputField.value = iconClass;
                preview.innerHTML = `<span style="font-weight:bold; color:#444;">Текущая иконка:</span> <i class="bi ${iconClass}" style="font-size: 28px; margin-left: 10px; color: #417690; vertical-align: middle;"></i>`;

                Array.from(container.children).forEach(child => {
                    child.style.border = "2px solid transparent";
                    child.style.background = "transparent";
                    child.style.color = "#555";
                });
                btn.style.border = "2px solid #417690";
                btn.style.background = "#e1eef4";
                btn.style.color = "#417690";
            });

            container.appendChild(btn);
        });
    }

    // 1. Ищем все поля иконок, которые УЖЕ есть на странице при загрузке (у них id заканчивается на -icon_class)
    document.querySelectorAll('input[id$="-icon_class"]').forEach(initIconPicker);

    // 2. Слушаем админку: если ты нажал "Добавить еще одну страницу", скрипт мгновенно нарисует там новые иконки
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Если это HTML-элемент
                    const inputs = node.querySelectorAll('input[id$="-icon_class"]');
                    inputs.forEach(initIconPicker);
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
});