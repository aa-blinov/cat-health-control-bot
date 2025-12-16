## Экран `main-menu`

### Назначение

Главное меню после входа в приложение. Даёт быстрый доступ ко всем основным действиям:
запись кормления, приступов астмы, дефекаций, смены лотка, измерения веса, просмотра истории и (для администратора) админ‑панели.

### Разметка и ключевые элементы

- Корневой контейнер дашборда: `div.dashboard` в шаблоне [`web/templates/dashboard.html`](web/templates/dashboard.html).
- Экран главного меню:
  - Контейнер: `div#main-menu.screen.active`
  - Внутри: `div.action-cards` — сетка action‑карточек.

Карточки действий:

- Кормление:
  - Элемент: `div.card.action-card.action-card-feeding`
  - Текст: `Дневная порция корма / Записать порцию`
  - Обработчик: `onclick="showScreen('feeding-form')"`
- Вес:
  - `div.card.action-card.action-card-weight`
  - `onclick="showScreen('weight-form')"`
- Приступ астмы:
  - `div.card.action-card.action-card-asthma`
  - `onclick="showScreen('asthma-form')"`
- Дефекация:
  - `div.card.action-card.action-card-defecation`
  - `onclick="showScreen('defecation-form')"`
- Смена лотка:
  - `div.card.action-card.action-card-litter`
  - `onclick="showScreen('litter-form')"`
- История:
  - `div.card.action-card.action-card-history`
  - `onclick="showScreen('history')"`
- Админ‑панель:
  - `div.card.action-card.action-card-admin.admin-link`
  - Изначально скрыта: `style="display: none;"`
  - `onclick="showScreen('admin-panel')"`

CSS для карточек:

- Используются классы:
  - `.action-cards`, `.card`, `.action-card-*` в [`web/static/css/style.css`](web/static/css/style.css).
  - Цветовые акценты и отступы у заголовка/описания задаются через `.action-card-xxx` и `.action-card-xxx .card-content` (в F7‑варианте), сейчас же применяются к простым `.card`/`.action-card`.

### JS‑логика и зависимости

- Навигация:
  - Все `onclick="showScreen('...')"` завязаны на глобальную функцию `showScreen`, определённую как обёртка над `NavigationModule.showScreen`:

```3:12:web/static/js/navigation.js
const NavigationModule = {
    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show selected screen
        const screen = document.getElementById(screenId);
        if (screen) {
            screen.classList.add('active');
            window.scrollTo(0, 0);
            // ... контекстно‑зависимая инициализация экранов ...
        }
    }
};

function showScreen(screenId) {
    return NavigationModule.showScreen(screenId);
}
```

- Доступность админ‑карточки:
  - Класс `.admin-link` используется и для карточки в `main-menu`, и для блока‑строки в более ранней F7‑версии.
  - Модуль `UsersModule` управляет видимостью админ‑карточки:

```5:23:web/static/js/users.js
async checkAdminStatus() {
    try {
        const response = await fetch('/api/users', { credentials: 'include' });
        this.isAdmin = response.ok;
        if (this.isAdmin) {
            const adminLink = document.querySelector('.admin-link');
            if (adminLink) adminLink.style.display = 'flex';
        } else {
            const adminLink = document.querySelector('.admin-link');
            if (adminLink) adminLink.style.display = 'none';
        }
        return this.isAdmin;
    } catch (error) {
        this.isAdmin = false;
        const adminLink = document.querySelector('.admin-link');
        if (adminLink) adminLink.style.display = 'none';
        return false;
    }
}
```

- Инициализация `checkAdminStatus` выполняется при загрузке `dashboard.html`:

```454:463:web/templates/dashboard.html
// Инициализируем модули
PetsModule.init();
const switcher = document.getElementById('pet-switcher');
if (switcher) {
    switcher.style.display = 'block';
}

UsersModule.checkAdminStatus().then(() => {
    return PetsModule.checkAndSelectPet();
});
```

### API и права доступа

- Права администратора определяются бэкендом:
  - Эндпоинт `/api/users` доступен только администратору (`@admin_required` в [`web/app.py`](web/app.py)).
  - Если ответ `/api/users` успешен (`response.ok`), фронтенд считает пользователя админом и показывает админ‑карточку.
- Если запрос `/api/users` падает (403, 401, 500) — админ‑карточка скрывается.

### Навигация между экранами

- Из `main-menu` можно перейти:
  - На любую из пяти форм записей (`*-form`), историю (`history`) и админ‑панель (`admin-panel`).
- При возврате со всех остальных экранов используется `back-btn` с `onclick="showScreen('main-menu')"`, так что `main-menu` является «домашним» экраном.

### Инварианты для будущего рефакторинга

1. **Идентификатор экрана**: должен сохраняться `id="main-menu"`, чтобы:
   - работали существующие `back-btn` (`showScreen('main-menu')`),
   - корректно отрабатывали любые внешние вызовы навигации.
2. **Класс `.admin-link`** должен остаться на админ‑элементе, чтобы `UsersModule.checkAdminStatus` продолжал управлять его видимостью.
3. **Клики по карточкам** должны либо:
   - напрямую вызывать `showScreen('...')`, либо
   - быть заменены на эквивалентную навигацию, но с сохранением всех соответствий:
     - feeding → `feeding-form`, asthma → `asthma-form`, defecation → `defecation-form`,
       litter → `litter-form`, weight → `weight-form`, history → `history`,
       admin → `admin-panel`.


