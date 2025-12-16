## Динамические формы: кормление, астма, дефекация, лоток, вес

Эти формы не прописаны статично в HTML, а генерируются на лету на основе конфигурации `FORM_CONFIGS`
в [`web/static/js/forms-config.js`](web/static/js/forms-config.js) и вставляются в контейнеры внутри
`dashboard.html`.

### Общая схема работы

1. При загрузке `dashboard.html`:
   - В `DOMContentLoaded` создаются формы для типов `feeding`, `asthma`, `defecation`, `litter`, `weight`:

```434:449:web/templates/dashboard.html
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем формы при загрузке
    const formTypes = ['feeding', 'asthma', 'defecation', 'litter', 'weight'];
    formTypes.forEach(formType => {
        const container = document.getElementById(`${formType}-form-container`);
        if (container) {
            container.innerHTML = createFormHTML(formType);
            const form = document.getElementById(`${formType}-form-element`);
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    handleFormSubmit(formType, form);
                });
            }
        }
    });
    
    resetFormDefaults();
    // ... init PetsModule, UsersModule ...
});
```

2. При навигации через `showScreen`:
   - При открытии любого `*-form` экран снова генерирует форму (с учётом `record_id` для редактирования) через `NavigationModule`:

```15:27:web/static/js/navigation.js
const formTypes = ['feeding', 'asthma', 'defecation', 'litter', 'weight'];
const formType = formTypes.find(type => screenId === `${type}-form`);

if (formType) {
    const container = document.getElementById(`${formType}-form-container`);
    if (container) {
        const formElement = document.getElementById(`${formType}-form-element`);
        const recordId = formElement ? formElement.querySelector('[name="record_id"]')?.value : null;

        if (typeof createFormHTML === 'function') {
            container.innerHTML = createFormHTML(formType, recordId);
            const newForm = document.getElementById(`${formType}-form-element`);
            if (newForm && typeof handleFormSubmit === 'function') {
                newForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    handleFormSubmit(formType, newForm);
                });
            }
            if (!recordId && typeof resetFormDefaults === 'function') {
                resetFormDefaults();
            }
        }
    }
}
```

3. Отправка формы:
   - Осуществляется единым обработчиком `handleFormSubmit(formType, formElement)`, который:
     - извлекает `pet_id` через `getSelectedPetId()`,
     - трансформирует поля в формат API через `config.transformData`,
     - отправляет JSON‑запрос на нужный эндпоинт.

```332:360:web/static/js/forms-config.js
async function handleFormSubmit(formType, formElement) {
    const config = FORM_CONFIGS[formType];
    if (!config) {
        showAlert('error', 'Неизвестный тип формы');
        return;
    }
    
    const formData = new FormData(formElement);
    const recordId = formData.get('record_id');
    const petId = getSelectedPetId();
    
    if (!petId) {
        showAlert('error', 'Выберите животное в меню навигации');
        return;
    }
    
    formData.set('pet_id', petId);
    const data = config.transformData(formData);
    
    try {
        const url = recordId ? `${config.endpoint}/${recordId}` : config.endpoint;
        const method = recordId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(data)
        });
        // ... обработка ответа ...
    } catch (error) {
        showAlert('error', 'Ошибка при сохранении');
    }
}
```

4. Значения по умолчанию:
   - При создании формы `createFormHTML` получает настройки через `getFormSettings()`, которые, в свою очередь,
     берут данные из `localStorage` или `SettingsModule.DEFAULT_SETTINGS`.
   - Отдельная функция `resetFormDefaults` в `dashboard.html` проставляет значения в уже существующие элементы
     (важно для случаев, когда форма пересоздаётся без перезагрузки страницы).

```452:474:web/templates/dashboard.html
function resetFormDefaults() {
    const now = new Date();
    const dateStr = `${year}-${month}-${day}`;
    const timeStr = now.toTimeString().slice(0, 5);
    const settings = getSettings();
    
    const formDefaults = {
        feeding: { date: dateStr, time: timeStr },
        asthma: { date: dateStr, time: timeStr,
            duration: settings.asthma.duration,
            inhalation: settings.asthma.inhalation,
            reason: settings.asthma.reason },
        defecation: { date: dateStr, time: timeStr,
            stool_type: settings.defecation.stool_type,
            color: settings.defecation.color || 'Коричневый',
            food: settings.defecation.food },
        litter: { date: dateStr, time: timeStr },
        weight: { date: dateStr, time: timeStr, food: settings.weight.food }
    };
    // ... проход по FORM_CONFIGS и установка element.value ...
}
```

### Конфигурация `FORM_CONFIGS`

`FORM_CONFIGS` описывает для каждого типа формы:

- заголовок (`title` — используется в F7‑/альтернативных UI),
- API‑эндпоинт (`endpoint`),
- список полей (`fields`),
- функцию трансформации данных (`transformData`),
- генератор сообщения об успехе (`successMessage`).

#### Общие поля

Каждое поле в `fields` имеет структуру:

- `name` — имя поля в данных/форме,
- `type` — тип ввода (`date`, `time`, `number`, `text`, `textarea`, `select`),
- `label` — подпись в UI,
- `required` — обязательность,
- дополнительные атрибуты (`placeholder`, `min`, `max`, `step`, `options`, `rows`, `id`).

`createFormHTML` использует эти данные, чтобы сгенерировать HTML (на текущий момент — через
legacy‑разметку `.inline-form` + `.form-group`, см. `createFieldHTML`).

#### Форма кормления (`feeding`)

- Контейнер экрана: `div#feeding-form.screen`, содержимое вставляется в `div#feeding-form-container`.
- Конфиг:

```4:21:web/static/js/forms-config.js
feeding: {
    title: 'Записать дневную порцию корма',
    endpoint: '/api/feeding',
    fields: [
        { name: 'date', type: 'date', label: 'Дата', required: true, id: 'feeding-date' },
        { name: 'time', type: 'time', label: 'Время', required: true, id: 'feeding-time' },
        { name: 'food_weight', type: 'number', label: 'Вес корма (граммы)',
          required: true, placeholder: '50', min: 0, step: 0.1, id: 'feeding-food-weight' },
        { name: 'comment', type: 'textarea', label: 'Комментарий (необязательно)',
          rows: 2, id: 'feeding-comment' }
    ],
    transformData: (formData) => ({
        pet_id: formData.get('pet_id'),
        date: formData.get('date'),
        time: formData.get('time'),
        food_weight: formData.get('food_weight'),
        comment: formData.get('comment') || ''
    }),
    successMessage: (isEdit) => isEdit ? 'Дневная порция обновлена' : 'Дневная порция записана'
}
```

- API:
  - Создание: `POST /api/feeding`
  - Обновление: `PUT /api/feeding/<record_id>`
  - Удаление: `DELETE /api/feeding/<record_id>`
  - Получение списка для истории: `GET /api/feeding?pet_id=...`
  - Экспорт: `GET /api/export/feeding/<format>?pet_id=...`

#### Форма астмы (`asthma`)

- Экран: `div#asthma-form.screen` + `div#asthma-form-container`.
- Конфиг:

```23:49:web/static/js/forms-config.js
asthma: {
    title: 'Записать приступ астмы',
    endpoint: '/api/asthma',
    fields: [
        { name: 'date', type: 'date', label: 'Дата', required: true, id: 'asthma-date' },
        { name: 'time', type: 'time', label: 'Время', required: true, id: 'asthma-time' },
        { name: 'duration', type: 'select', label: 'Длительность', required: true,
          options: [{ value: 'Короткий', text: 'Короткий' },
                    { value: 'Длительный', text: 'Длительный' }],
          value: 'Короткий', id: 'asthma-duration' },
        { name: 'inhalation', type: 'select', label: 'Ингаляция', required: true,
          options: [{ value: 'false', text: 'Нет' },
                    { value: 'true', text: 'Да' }],
          value: 'false', id: 'asthma-inhalation' },
        { name: 'reason', type: 'text', label: 'Причина', required: true,
          placeholder: 'Пил после сна', value: 'Пил', id: 'asthma-reason' },
        { name: 'comment', type: 'textarea', label: 'Комментарий (необязательно)',
          rows: 2, id: 'asthma-comment' }
    ],
    transformData: (formData) => ({
        pet_id: formData.get('pet_id'),
        date: formData.get('date'),
        time: formData.get('time'),
        duration: formData.get('duration'),
        reason: formData.get('reason'),
        inhalation: formData.get('inhalation') === 'true',
        comment: formData.get('comment') || ''
    }),
    successMessage: (isEdit) => isEdit ? 'Приступ астмы обновлен' : 'Приступ астмы записан'
}
```

- Особенности:
  - В истории бэкенд преобразует логическое `inhalation` в строки `"Да"/"Нет"`:

```1565:1572:web/app.py
if attack.get("inhalation") is True:
    attack["inhalation"] = "Да"
elif attack.get("inhalation") is False:
    attack["inhalation"] = "Нет"
```

  - При редактировании записи `editRecord` в `dashboard.html` делает обратное преобразование, чтобы поле селекта правильно отобразилось:

```1005:1010:web/templates/dashboard.html
const formRecord = { ...record };
if (type === 'asthma' && record.inhalation === 'Да') {
    formRecord.inhalation = 'true';
} else if (type === 'asthma' && record.inhalation === 'Нет') {
    formRecord.inhalation = 'false';
}
populateForm(type, formRecord, recordId);
```

- API:
  - Аналогично кормлению: `/api/asthma` (`POST`, `GET`), `/api/asthma/<record_id>` (`PUT`, `DELETE`), экспорт через `/api/export/asthma/...`.

#### Форма дефекации (`defecation`)

- Экран: `div#defecation-form.screen` + `div#defecation-form-container`.
- Конфиг:

```51:80:web/static/js/forms-config.js
defecation: {
    title: 'Записать дефекацию',
    endpoint: '/api/defecation',
    fields: [
        { name: 'date', type: 'date', label: 'Дата', required: true, id: 'defecation-date' },
        { name: 'time', type: 'time', label: 'Время', required: true, id: 'defecation-time' },
        { name: 'stool_type', type: 'select', label: 'Тип стула', required: true,
          options: [...], value: 'Обычный', id: 'defecation-stool-type' },
        { name: 'color', type: 'select', label: 'Цвет стула', required: true,
          options: [...], value: 'Коричневый', id: 'defecation-color' },
        { name: 'food', type: 'text', label: 'Корм',
          placeholder: 'Royal Canin Fibre Response',
          value: 'Royal Canin Fibre Response', id: 'defecation-food' },
        { name: 'comment', type: 'textarea', label: 'Комментарий (необязательно)', rows: 2,
          id: 'defecation-comment' }
    ],
    transformData: (formData) => ({
        pet_id: formData.get('pet_id'),
        date: formData.get('date'),
        time: formData.get('time'),
        stool_type: formData.get('stool_type'),
        color: formData.get('color'),
        food: formData.get('food') || '',
        comment: formData.get('comment') || ''
    }),
    successMessage: (isEdit) => isEdit ? 'Дефекация обновлена' : 'Дефекация записана'
}
```

- API:
  - `POST/GET /api/defecation`, `PUT/DELETE /api/defecation/<record_id>`, экспорт `/api/export/defecation/...`.

#### Форма смены лотка (`litter`)

- Экран: `div#litter-form.screen` + `div#litter-form-container`.
- Конфиг:

```82:97:web/static/js/forms-config.js
litter: {
    title: 'Записать смену лотка',
    endpoint: '/api/litter',
    fields: [
        { name: 'date', type: 'date', label: 'Дата', required: true, id: 'litter-date' },
        { name: 'time', type: 'time', label: 'Время', required: true, id: 'litter-time' },
        { name: 'comment', type: 'textarea', label: 'Комментарий (необязательно)',
          rows: 3, placeholder: 'Полная замена наполнителя', id: 'litter-comment' }
    ],
    transformData: (formData) => ({
        pet_id: formData.get('pet_id'),
        date: formData.get('date'),
        time: formData.get('time'),
        comment: formData.get('comment') || ''
    }),
    successMessage: (isEdit) => isEdit ? 'Смена лотка обновлена' : 'Смена лотка записана'
}
```

- API:
  - `POST/GET /api/litter`, `PUT/DELETE /api/litter/<record_id>`, экспорт `/api/export/litter/...`.

#### Форма веса (`weight`)

- Экран: `div#weight-form.screen` + `div#weight-form-container`.
- Конфиг:

```98:116:web/static/js/forms-config.js
weight: {
    title: 'Записать вес',
    endpoint: '/api/weight',
    fields: [
        { name: 'date', type: 'date', label: 'Дата', required: true, id: 'weight-date' },
        { name: 'time', type: 'time', label: 'Время', required: true, id: 'weight-time' },
        { name: 'weight', type: 'number', label: 'Вес (кг)', required: true,
          placeholder: '4.5', step: 0.01, min: 0, max: 20, id: 'weight-value' },
        { name: 'food', type: 'text', label: 'Корм',
          placeholder: 'Royal Canin Fibre Response',
          value: 'Royal Canin Fibre Response', id: 'weight-food' },
        { name: 'comment', type: 'textarea', label: 'Комментарий (необязательно)',
          rows: 2, id: 'weight-comment' }
    ],
    transformData: (formData) => ({
        pet_id: formData.get('pet_id'),
        date: formData.get('date'),
        time: formData.get('time'),
        weight: formData.get('weight'),
        food: formData.get('food') || '',
        comment: formData.get('comment') || ''
    }),
    successMessage: (isEdit) => isEdit ? 'Вес обновлен' : 'Вес записан'
}
```

- API:
  - `POST/GET /api/weight`, `PUT/DELETE /api/weight/<record_id>`, экспорт `/api/export/weight/...`.

### Инварианты для будущего рефакторинга

1. **ID контейнеров**: `#feeding-form-container`, `#asthma-form-container`, `#defecation-form-container`,
   `#litter-form-container`, `#weight-form-container` должны существовать, чтобы `createFormHTML` мог
   корректно вставить разметку.
2. **ID форм**: формы должны иметь `id="${formType}-form-element"` и скрытое поле `name="record_id"`,
   чтобы редактирование (`populateForm`) и `NavigationModule` корректно определяли режим редактирования.
3. **Использование `FORM_CONFIGS`**: при переходе на новый UI (например, F7) рекомендуется не трогать
   структуру `FORM_CONFIGS` и `transformData`, а лишь изменить реализацию `createFormHTML`/`createFieldHTML`
   и стили.
4. **Значения по умолчанию**:
   - Источником истины остаётся `SettingsModule.DEFAULT_SETTINGS` + данные из `localStorage`.
   - Любой новый UI должен по-прежнему использовать `getFormSettings()/getSettings()` и `resetFormDefaults`,
     чтобы не сломать логику настроек.


