## Экран `settings` — настройки значений по умолчанию

### Назначение

Экран позволяет пользователю настраивать значения по умолчанию для форм:

- приступов астмы,
- дефекаций,
- измерений веса.

Эти настройки сохраняются в `localStorage` и используются как начальные значения в динамических формах.

### Разметка и ключевые элементы

- Экран:
  - Контейнер: `div#settings.screen` в [`web/templates/dashboard.html`](web/templates/dashboard.html).
  - Заголовок:

```92:97:web/templates/dashboard.html
<div id="settings" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('main-menu')">← Назад</button>
        <h2>Настройки значений по умолчанию</h2>
    </div>
```

- Форма:

```98:160:web/templates/dashboard.html
<form id="settings-form" class="inline-form">
    <div class="form-content">
        <div class="settings-section">
            <h3>Приступ астмы</h3>
            <div class="form-group">
                <label for="default-asthma-duration">Длительность по умолчанию</label>
                <select id="default-asthma-duration" name="default_asthma_duration">...</select>
            </div>
            <div class="form-group">
                <label for="default-asthma-inhalation">Ингаляция по умолчанию</label>
                <select id="default-asthma-inhalation" name="default_asthma_inhalation">...</select>
            </div>
            <div class="form-group">
                <label for="default-asthma-reason">Причина по умолчанию</label>
                <input type="text" id="default-asthma-reason" name="default_asthma_reason" placeholder="Пил">
            </div>
        </div>
        <div class="settings-section">
            <h3>Дефекация</h3>
            <div class="form-group">
                <label for="default-defecation-stool-type">Тип стула по умолчанию</label>
                <select id="default-defecation-stool-type" name="default_defecation_stool_type">...</select>
            </div>
            <div class="form-group">
                <label for="default-defecation-color">Цвет стула по умолчанию</label>
                <select id="default-defecation-color" name="default_defecation_color">...</select>
            </div>
            <div class="form-group">
                <label for="default-defecation-food">Корм по умолчанию</label>
                <input type="text" id="default-defecation-food" name="default_defecation_food"
                       placeholder="Royal Canin Fibre Response">
            </div>
        </div>
        <div class="settings-section">
            <h3>Вес</h3>
            <div class="form-group">
                <label for="default-weight-food">Корм по умолчанию</label>
                <input type="text" id="default-weight-food" name="default_weight_food"
                       placeholder="Royal Canin Fibre Response">
            </div>
        </div>
    </div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary btn-block">Сохранить настройки</button>
        <button type="button" class="btn btn-secondary btn-block" onclick="resetSettingsToDefaults()">
            Сбросить к значениям по умолчанию
        </button>
    </div>
</form>
```

### JS‑логика и зависимости

#### Модуль `SettingsModule`

Файл [`web/static/js/settings.js`](web/static/js/settings.js) определяет модуль настроек:

- Источник значений по умолчанию:

```2:17:web/static/js/settings.js
const SettingsModule = {
    DEFAULT_SETTINGS: {
        asthma: {
            duration: 'Короткий',
            inhalation: 'false',
            reason: 'Пил'
        },
        defecation: {
            stool_type: 'Обычный',
            color: 'Коричневый',
            food: 'Royal Canin Fibre Response'
        },
        weight: {
            food: 'Royal Canin Fibre Response'
        }
    },
    // ...
}
```

- Загрузка/сохранение настроек:

```19:38:web/static/js/settings.js
loadSettings() {
    const saved = localStorage.getItem('formDefaults');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            if (settings.defecation && !settings.defecation.color) {
                settings.defecation.color = 'Коричневый';
            }
            return settings;
        } catch (e) {
            console.error('Error loading settings:', e);
        }
    }
    return this.DEFAULT_SETTINGS;
},

saveSettings(settings) {
    localStorage.setItem('formDefaults', JSON.stringify(settings));
},
```

- Применение настроек к форме:

```44:52:web/static/js/settings.js
loadSettingsForm() {
    const settings = this.getSettings();
    document.getElementById('default-asthma-duration').value = settings.asthma.duration;
    document.getElementById('default-asthma-inhalation').value = settings.asthma.inhalation;
    document.getElementById('default-asthma-reason').value = settings.asthma.reason;
    document.getElementById('default-defecation-stool-type').value = settings.defecation.stool_type;
    document.getElementById('default-defecation-color').value = settings.defecation.color || 'Коричневый';
    document.getElementById('default-defecation-food').value = settings.defecation.food;
    document.getElementById('default-weight-food').value = settings.weight.food;
},
```

- Сброс к значениям по умолчанию:

```55:62:web/static/js/settings.js
resetSettingsToDefaults() {
    if (confirm('Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?')) {
        this.saveSettings(this.DEFAULT_SETTINGS);
        this.loadSettingsForm();
        if (typeof showAlert === 'function') {
            showAlert('success', 'Настройки сброшены к значениям по умолчанию');
        }
    }
}
```

- Глобальные обёртки:

```67:86:web/static/js/settings.js
const DEFAULT_SETTINGS = SettingsModule.DEFAULT_SETTINGS;
function loadSettings() { return SettingsModule.loadSettings(); }
function saveSettings(settings) { return SettingsModule.saveSettings(settings); }
function getSettings() { return SettingsModule.getSettings(); }
function loadSettingsForm() { return SettingsModule.loadSettingsForm(); }
function resetSettingsToDefaults() { return SettingsModule.resetSettingsToDefaults(); }
```

#### Обработчик отправки формы настроек

Внизу `dashboard.html`:

```812:836:web/templates/dashboard.html
document.getElementById('settings-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const settings = {
        asthma: {
            duration: document.getElementById('default-asthma-duration').value,
            inhalation: document.getElementById('default-asthma-inhalation').value,
            reason: document.getElementById('default-asthma-reason').value
        },
        defecation: {
            stool_type: document.getElementById('default-defecation-stool-type').value,
            color: document.getElementById('default-defecation-color').value,
            food: document.getElementById('default-defecation-food').value
        },
        weight: {
            food: document.getElementById('default-weight-food').value
        }
    };
    
    saveSettings(settings);
    showAlert('success', 'Настройки сохранены');
    setTimeout(() => {
        showScreen('main-menu');
    }, 500);
});
```

#### Связь с динамическими формами

- `FORMS_CONFIGS` использует `getFormSettings()`:

```120:139:web/static/js/forms-config.js
function getFormSettings() {
    try {
        const saved = localStorage.getItem('formDefaults');
        if (saved) {
            const settings = JSON.parse(saved);
            if (settings.defecation && !settings.defecation.color) {
                settings.defecation.color = 'Коричневый';
            }
            return settings;
        }
    } catch (e) {
        console.error('Error loading settings:', e);
    }
    if (typeof SettingsModule !== 'undefined' && SettingsModule.DEFAULT_SETTINGS) {
        return SettingsModule.DEFAULT_SETTINGS;
    }
    // Fallback (дублирует DEFAULT_SETTINGS на случай отсутствия модуля)
    return { ... };
}
```

- `createFormHTML` использует эти настройки для инициализации полей (кроме даты/времени, для которых берётся «сейчас»).
- `resetFormDefaults` в `dashboard.html` повторно применяет их к уже существующим DOM‑элементам форм.

### Навигация

- Переход на экран:
  - Через кнопку ⚙️ в навбаре (в `base.html`), `onclick="showScreen('settings')"`.
  - Функция `NavigationModule.showScreen('settings')` при открытии экрана вызывает `loadSettingsForm()`,
    чтобы подтянуть актуальные значения:

```44:47:web/static/js/navigation.js
} else if (screenId === 'settings') {
    if (typeof loadSettingsForm === 'function') {
        loadSettingsForm();
    }
}
```

- Возврат:
  - Через `back-btn` `onclick="showScreen('main-menu')"` либо после сохранения (через `setTimeout`).

### Инварианты для рефакторинга

1. **ID полей**: `default-asthma-duration`, `default-asthma-inhalation`, `default-asthma-reason`,
   `default-defecation-stool-type`, `default-defecation-color`, `default-defecation-food`,
   `default-weight-food` — должны быть сохранены, если логика `SettingsModule` и `resetFormDefaults`
   остаётся неизменной.
2. **Структура объекта настроек**:
   - Формат в `localStorage` (`formDefaults`) и в `SettingsModule.DEFAULT_SETTINGS`:
     - `settings.asthma.duration`, `settings.asthma.inhalation`, `settings.asthma.reason`
     - `settings.defecation.stool_type`, `settings.defecation.color`, `settings.defecation.food`
     - `settings.weight.food`
   - Любые изменения структуры потребуют синхронной правки:
     - `SettingsModule.loadSettingsForm`,
     - `dashboard.html::resetFormDefaults`,
     - `forms-config.js::getFormSettings`.
3. **Механизм хранения**:
   - Все настройки по умолчанию хранятся только в `localStorage` (`formDefaults`), сервер о них не знает.
   - При рефакторинге нельзя полагаться на бэкенд как на источник этих дефолтов без изменения API.


