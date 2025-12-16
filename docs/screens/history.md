## Экран `history` — история записей и экспорт данных

### Назначение

Экран позволяет:

- просматривать историю записей по питомцу, разделённую по типам:
  - дневные порции корма,
  - приступы астмы,
  - дефекации,
  - смены лотка,
  - вес;
- редактировать/удалять отдельные записи;
- выгружать данные в различные форматы (CSV, TSV, HTML, Markdown).

Основная логика в модуле [`web/static/js/history.js`](web/static/js/history.js) и внизу `dashboard.html`.

---

## Разметка экрана

```331:368:web/templates/dashboard.html
<div id="history" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('main-menu')">← Назад</button>
        <h2>История записей</h2>
        <div class="export-buttons">
            <button class="btn btn-secondary btn-small" onclick="showExportMenu()">Выгрузить</button>
        </div>
    </div>
    <div id="export-menu" class="export-menu" style="display: none;"
         onclick="if(event.target === this) hideExportMenu()">
        <div class="export-menu-content">
            <h3 id="export-menu-title">Выберите тип данных:</h3>
            <div id="export-type-selection" class="export-options">
                <button class="btn btn-secondary btn-block" onclick="selectExportType('feeding')">Дневные порции</button>
                <button class="btn btn-secondary btn-block" onclick="selectExportType('weight')">Вес</button>
                <button class="btn btn-secondary btn-block" onclick="selectExportType('asthma')">Приступы астмы</button>
                <button class="btn btn-secondary btn-block" onclick="selectExportType('defecation')">Дефекации</button>
                <button class="btn btn-secondary btn-block" onclick="selectExportType('litter')">Смена лотка</button>
            </div>
            <div id="export-format-selection" class="export-options" style="display: none;">
                <button class="btn btn-secondary btn-block" onclick="exportData('csv')">CSV</button>
                <button class="btn btn-secondary btn-block" onclick="exportData('tsv')">TSV</button>
                <button class="btn btn-secondary btn-block" onclick="exportData('html')">HTML</button>
                <button class="btn btn-secondary btn-block" onclick="exportData('md')">Markdown</button>
            </div>
            <button id="export-back-btn" class="btn btn-primary btn-block"
                    onclick="backToExportType()" style="display: none;">Назад</button>
            <button id="export-cancel-btn" class="btn btn-primary btn-block"
                    onclick="hideExportMenu()">Отмена</button>
        </div>
    </div>
    <div class="history-tabs">
        <button class="tab-btn active" data-tab="feeding"
                onclick="showHistoryTab('feeding'); return false;">Дневные порции</button>
        <button class="tab-btn" data-tab="weight"
                onclick="showHistoryTab('weight'); return false;">Вес</button>
        <button class="tab-btn" data-tab="asthma"
                onclick="showHistoryTab('asthma'); return false;">Приступы астмы</button>
        <button class="tab-btn" data-tab="defecation"
                onclick="showHistoryTab('defecation'); return false;">Дефекации</button>
        <button class="tab-btn" data-tab="litter"
                onclick="showHistoryTab('litter'); return false;">Смена лотка</button>
    </div>
    <div id="history-content" class="history-content">
        <div class="loading">Загрузка...</div>
    </div>
</div>
```

Список записей вставляется в `#history-content` как `div.history-list` с множеством `.history-item`.

---

## Модуль `HistoryModule`

Файл [`web/static/js/history.js`](web/static/js/history.js).

### Конфигурация типов записей

```2:79:web/static/js/history.js
const HistoryModule = {
    currentHistoryType: 'asthma',
    selectedExportType: null,

    typeConfig: {
        feeding: {
            endpoint: 'feeding',
            dataKey: 'feedings',
            displayName: 'Дневные порции',
            renderDetails: (item) => { ... }
        },
        asthma: {
            endpoint: 'asthma',
            dataKey: 'attacks',
            displayName: 'Приступы астмы',
            renderDetails: (item) => { ... }
        },
        defecation: {
            endpoint: 'defecation',
            dataKey: 'defecations',
            displayName: 'Дефекации',
            renderDetails: (item) => { ... }
        },
        litter: {
            endpoint: 'litter',
            dataKey: 'litter_changes',
            displayName: 'Смена лотка',
            renderDetails: (item) => { ... }
        },
        weight: {
            endpoint: 'weight',
            dataKey: 'weights',
            displayName: 'Вес',
            renderDetails: (item) => { ... }
        }
    },
    // ...
}
```

Каждый тип знает:

- имя эндпоинта (без `/api/`),
- ключ массива в JSON‑ответе (например, `feedings`),
- отображаемое имя вкладки,
- функцию, которая строит HTML деталей записи (`renderDetails`).

### Форматирование даты/времени

```81:89:web/static/js/history.js
formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    const [datePart, timePart] = dateTimeStr.split(' ');
    const [year, month, day] = datePart.split('-');
    return `${day}.${month}.${year} ${timePart}`;
}
```

---

## Переключение вкладок и загрузка истории

### Функция `showHistoryTab(type)`

```92:156:web/static/js/history.js
showHistoryTab(type) {
    this.currentHistoryType = type;
    const config = this.typeConfig[type];
    if (!config) return;

    // Обновление .tab-btn
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        const isMatch = btn.textContent.includes(config.displayName);
        if (isMatch) btn.classList.add('active');
    });

    const content = document.getElementById('history-content');
    const petId = typeof getSelectedPetId === 'function' ? getSelectedPetId() : null;
    if (!petId) {
        content.innerHTML = '<div class="empty-state"><p>Выберите животное в меню навигации для просмотра истории</p></div>';
        return;
    }

    content.innerHTML = '<div class="loading">Загрузка...</div>';
    const endpoint = `/api/${config.endpoint}?pet_id=${petId}`;

    fetch(endpoint, { credentials: 'include' })
        .then(response => { ... проверка ошибок ... })
        .then(data => {
            const items = data[config.dataKey] || [];
            if (!items.length) {
                content.innerHTML = '<p class="no-data">Нет записей</p>';
                return;
            }
            let html = '<div class="history-list">';
            items.forEach(item => {
                html += `<div class="history-item history-item-${type}" data-id="${item._id}">`;
                html += `<div class="history-date">${this.formatDateTime(item.date_time)}</div>`;
                const username = item.username || '-';
                html += `<div class="history-user"><strong>Пользователь:</strong> ${username}</div>`;
                html += `<div class="history-details">${config.renderDetails(item)}</div>`;
                html += `<div class="history-actions">`;
                html += `<button class="btn btn-secondary btn-small" onclick="editRecord('${type}', '${item._id}')">Редактировать</button>`;
                html += `<button class="btn btn-secondary btn-small" onclick="deleteRecord('${type}', '${item._id}')">Удалить</button>`;
                html += `</div></div>`;
            });
            html += '</div>';
            content.innerHTML = html;
        })
        .catch(error => {
            content.innerHTML = '<p class="error">Ошибка загрузки данных</p>';
        });
}
```

### Редактирование и удаление записей

Эти функции описаны в `dashboard.html`:

- `editRecord(type, recordId)`:
  - загружает список записей по соответствующему эндпоинту (`/api/feeding`, `/api/asthma` и т.д.),
  - ищет запись по `_id`,
  - подготавливает данные для `populateForm(formType, recordData, recordId)` (в т.ч. преобразует `inhalation` для астмы),
  - переключает экран на соответствующую форму `showScreen('${type}-form')`.

- `deleteRecord(type, recordId)`:
  - бьёт по `/api/<type>/<record_id>` (`DELETE`),
  - при успехе вызывает `showHistoryTab(...)` для текущего выбранного таба, чтобы обновить UI.

---

## Экспорт данных

### UI‑поток

1. Клик по кнопке «Выгрузить» (`showExportMenu()`):
   - отображает модальное окно `#export-menu`,
   - показывает список типов (`#export-type-selection`) и скрывает выбор формата.

2. Клик по типу данных (`selectExportType(type)`):
   - сохраняет выбранный тип в `HistoryModule.selectedExportType`,
   - скрывает блок типов и показывает блок `#export-format-selection`,
   - меняет заголовок на `"Выберите формат (<тип>)"`,
   - отображает кнопку «Назад» (`#export-back-btn`), скрывает «Отмена».

3. Клик по формату (`exportData(format)`):
   - формирует URL `/api/export/<endpoint>/<format>?pet_id=...`,
   - скачивает файл, используя blob‑URL.

4. Кнопки:
   - «Назад» — `backToExportType()`.
   - «Отмена» и клик по фону модалки — `hideExportMenu()`.

### Реализация в `HistoryModule`

```158:192:web/static/js/history.js
showExportMenu() { ... }
hideExportMenu() { ... }
selectExportType(type) { ... }
backToExportType() { ... }
```

- Основной экспорт:

```194:260:web/static/js/history.js
async exportData(format) {
    if (!this.selectedExportType) {
        showAlert('error', 'Выберите тип данных');
        return;
    }
    const petId = getSelectedPetId();
    if (!petId) {
        showAlert('error', 'Выберите животное');
        return;
    }
    const config = this.typeConfig[this.selectedExportType];
    const url = `/api/export/${config.endpoint}/${format}?pet_id=${petId}`;

    const response = await fetch(url, { method: 'GET', credentials: 'include' });
    // ... проверка ошибок ...
    const contentDisposition = response.headers.get('Content-Disposition');
    // Извлечение имени файла
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    // ...
    this.hideExportMenu();
    showAlert('success', 'Файл выгружен');
}
```

### Бэкенд‑экспорт

Эндпоинт [`/api/export/<export_type>/<format_type>`](web/app.py) в `app.py`:

- Принимает:
  - `export_type` ∈ {`feeding`, `asthma`, `defecation`, `litter`, `weight`},
  - `format_type` ∈ {`csv`, `tsv`, `html`, `md`},
  - `pet_id` в query string.
- Проверяет:
  - наличие и корректность `pet_id`,
  - авторизацию и доступ к питомцу (`check_pet_access`).
- Собирает записи соответствующей коллекции (`feedings`, `asthma_attacks`, `defecations`, `litter_changes`, `weights`),
  форматирует и возвращает файл:
  - CSV/TSV — через `csv.writer`,
  - HTML — небольшая таблица с тёмной темой,
  - Markdown — таблица.
- Имя файла формируется на основе заголовка и текущей даты/времени.

---

## Навигация

- Вход в экран:
  - Из главного меню: `onclick="showScreen('history')"`.
  - `NavigationModule.showScreen('history')` при открытии сразу вызывает `showHistoryTab('feeding')`:

```70:73:web/static/js/navigation.js
} else if (screenId === 'history') {
    if (typeof showHistoryTab === 'function') {
        showHistoryTab('feeding');
    }
}
```

- Обновление при смене питомца:
  - В `PetsModule.setSelectedPet` при активном экране `history` повторно вызывается
    `showHistoryTab` для текущего таба.

---

## Инварианты для рефакторинга

1. **ID элементов**:
   - `#history`, `#history-content`, `#export-menu`, `#export-type-selection`, `#export-format-selection`,
     `#export-back-btn`, `#export-cancel-btn` должны существовать для работы `HistoryModule`.
2. **Классы вкладок**:
   - Кнопки табов должны оставаться `.tab-btn` с текстами, содержащими `displayName` из `typeConfig`,
     либо потребуется изменить логику определения активной вкладки.
3. **Соответствие типов и эндпоинтов**:
   - Связь `typeConfig.endpoint` ↔ API (`/api/<endpoint>`, `/api/export/<endpoint>/...`) — критична.
4. **Поведение кнопок «Редактировать» и «Удалить»**:
   - Должны продолжать вызывать глобальные функции `editRecord(type, id)` и `deleteRecord(type, id)`,
     либо эти функции нужно адаптировать вместе с UI.


