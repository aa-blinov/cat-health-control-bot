## Экраны питомцев: `pet-selector` и `pet-form`

### Общая роль

Этот блок экранов отвечает за:

- управление списком питомцев (создание, редактирование, удаление),
- выбор «текущего» питомца для всех форм/истории,
- управление доступом к питомцу (через вложенный блок доступа в `pet-form` и отдельный экран `pet-sharing`).

Основная логика вынесена в модуль [`web/static/js/pets.js`](web/static/js/pets.js).

---

## Экран `pet-selector` — список питомцев

### Разметка

- Контейнер:

```163:178:web/templates/dashboard.html
<div id="pet-selector" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('main-menu')">← Назад</button>
        <h2>Управление питомцами</h2>
    </div>
    <div class="inline-form">
        <div class="form-content">
            <div id="pets-list" class="pets-list">
                <div class="loading">Загрузка...</div>
            </div>
        </div>
        <div class="form-actions">
            <button class="btn btn-primary btn-block"
                    onclick="resetPetForm(); showScreen('pet-form');">+ Добавить питомца</button>
        </div>
    </div>
</div>
```

- `#pets-list` — сюда `PetsModule.renderPetsList()` отрисовывает карточки питомцев.

Структура карточек:

```69:88:web/static/js/pets.js
let html = '<div class="pets-grid">';
pets.forEach(pet => {
    const photo = pet.photo_url ? pet.photo_url + '?t=' + new Date().getTime() : '';
    const isOwner = pet.current_user_is_owner || false;
    html += `
        <div class="pet-card">
            <div class="pet-card-content" onclick="PetsModule.selectPet('${pet._id}', '${pet.name}')">
                ${photo ? `<img src="${photo}" alt="${pet.name}" class="pet-photo">`
                        : '<div class="pet-photo-placeholder">🐱</div>'}
                <div class="pet-info">
                    <h3>${pet.name}</h3>
                    ${pet.breed ? `<p>${pet.breed}</p>` : ''}
                    ${pet.gender ? `<p>${pet.gender}</p>` : ''}
                </div>
            </div>
            <div class="pet-card-actions">
                <button class="btn btn-secondary btn-small"
                        onclick="event.stopPropagation(); PetsModule.editPet('${pet._id}')">Редактировать</button>
                ${isOwner ? `<button class="btn btn-secondary btn-small"
                        onclick="event.stopPropagation(); PetsModule.showPetSharing('${pet._id}', '${pet.name}')">Доступ</button>` : ''}
            </div>
        </div>
    `;
});
html += '</div>';
container.innerHTML = html;
```

### JS‑логика: загрузка/выбор питомцев

Основные функции `PetsModule`:

- `loadPets()` — `GET /api/pets`, возвращает список питомцев, где текущий пользователь:
  - владелец (`owner`) или
  - имеет доступ через `shared_with`.

- `renderPetsList()` — отрисовывает содержимое `#pets-list` (см. выше).

- `selectPet(petId, petName)`:

```94:127:web/static/js/pets.js
selectPet(petId, petName) {
    this.setSelectedPet(petId, petName);
    this.updatePetSwitcher();
    
    const activeScreen = document.querySelector('.screen.active');
    const isInForm = activeScreen && (
        activeScreen.id === 'asthma-form' || 
        activeScreen.id === 'defecation-form' ||
        activeScreen.id === 'litter-form' ||
        activeScreen.id === 'weight-form' ||
        activeScreen.id === 'feeding-form' ||
        activeScreen.id === 'pet-form' ||
        activeScreen.id === 'user-form'
    );
    const isInHistory = activeScreen && activeScreen.id === 'history';
    const isInAdminPanel = activeScreen && activeScreen.id === 'admin-panel';
    const isInPetSelector = activeScreen && activeScreen.id === 'pet-selector';
    const isInPetSharing = activeScreen && activeScreen.id === 'pet-sharing';
    
    if (isInForm) {
        // остаёмся на форме
    } else if (isInHistory && typeof showHistoryTab === 'function') {
        const currentTab = document.querySelector('.tab-btn.active');
        if (currentTab) {
            const tabType = currentTab.getAttribute('data-tab');
            if (tabType) {
                showHistoryTab(tabType);
            }
        }
    } else if (isInAdminPanel || isInPetSelector || isInPetSharing) {
        // остаёмся на текущем экране
    } else if (typeof showScreen === 'function') {
        showScreen('main-menu');
    }
}
```

- `setSelectedPet(petId, petName)`:
  - сохраняет `petId` и имя в `localStorage`,
  - обновляет `pet-switcher` (компонент в навбаре),
  - при необходимости обновляет экран истории.

- `checkAndSelectPet()`:
  - проверяет, существует ли сохранённый питомец (запрос `/api/pets/<id>`),
  - если да — делает его выбранным и обновляет `pet-switcher`.

### Связь с навбаром (`pet-switcher`)

- В `base.html` (не приводится целиком): блок `#pet-switcher` и `#pet-switcher-menu`.
- `PetsModule.updatePetSwitcher()` обновляет имя выбранного питомца:

```130:141:web/static/js/pets.js
updatePetSwitcher() {
    const switcher = document.getElementById('pet-switcher');
    const switcherName = document.getElementById('pet-switcher-name');
    if (switcher && switcherName) {
        switcher.style.display = 'block';
        if (this.selectedPetId && this.selectedPetName) {
            switcherName.textContent = this.selectedPetName;
        } else {
            switcherName.textContent = 'Выбрать животное';
        }
    }
}
```

- `showPetSwitcherMenu()`/`hidePetSwitcherMenu()` — раскрывают меню выбора питомца в навбаре и наполняют его кнопками, которые вызывают `selectPet(...)`.

Глобальные обёртки обеспечивают совместимость с `onclick` и другими модулями:

```382:405:web/static/js/pets.js
function getSelectedPetId() { return PetsModule.getSelectedPetId(); }
function setSelectedPet(petId, petName) { return PetsModule.setSelectedPet(petId, petName); }
function selectPet(petId, petName) { return PetsModule.selectPet(petId, petName); }
function showPetSwitcherMenu() { return PetsModule.showPetSwitcherMenu(); }
function hidePetSwitcherMenu() { return PetsModule.hidePetSwitcherMenu(); }
function resetPetForm() { return PetsModule.resetPetForm(); }
// ...
```

---

## Экран `pet-form` — создание/редактирование питомца

### Разметка

- Контейнер:

```181:245:web/templates/dashboard.html
<div id="pet-form" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('pet-selector')">← Назад</button>
        <h2 id="pet-form-title">Добавить питомца</h2>
    </div>
    <form id="pet-form-element" class="inline-form">
        <input type="hidden" id="pet-record-id" name="pet_id" value="">
        <div class="form-content">
            <div class="form-group">
                <label for="pet-name">Имя *</label>
                <input type="text" id="pet-name" name="name" required placeholder="Саймон">
            </div>
            <div class="form-group">
                <label for="pet-breed">Порода</label>
                <input type="text" id="pet-breed" name="breed" placeholder="Британская короткошерстная">
            </div>
            <div class="form-group">
                <label for="pet-birth-date">Дата рождения</label>
                <input type="date" id="pet-birth-date" name="birth_date">
            </div>
            <div class="form-group">
                <label for="pet-gender">Пол</label>
                <select id="pet-gender" name="gender">...</select>
            </div>
            <div class="form-group">
                <label for="pet-photo-file">Фото питомца</label>
                <input type="file" id="pet-photo-file" name="photo_file" accept="image/*">
                <div id="pet-photo-preview" class="photo-preview-section" style="display: none;">
                    <img id="pet-photo-preview-img" src="" alt="Preview">
                    <button type="button" class="btn btn-secondary btn-small" onclick="clearPetPhoto()">Удалить фото</button>
                </div>
                <div id="pet-photo-current" class="photo-current-section" style="display: none;">
                    <h4>Текущее фото</h4>
                    <img id="pet-photo-current-img" src="" alt="Current">
                </div>
            </div>
            <div id="pet-access-section" class="sharing-section"
                 style="display: none; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 0.5px solid var(--ios-separator);">
                <h3>Управление доступом</h3>
                <div id="pet-shared-with-list" class="shared-list">
                    <div class="loading">Загрузка...</div>
                </div>
                <div class="form-group">
                    <label for="share-username-input">Поделиться с пользователем</label>
                    <div class="share-input-group">
                        <input type="text" id="share-username-input" placeholder="Введите имя пользователя">
                        <button type="button" class="btn btn-primary" onclick="sharePetFromForm()">Поделиться</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-block" id="pet-submit-btn">Сохранить</button>
            <button type="button" class="btn btn-secondary btn-block"
                    onclick="showScreen('pet-selector')">Отмена</button>
        </div>
    </form>
</div>
```

### JS‑логика: создание/редактирование питомца

#### Загрузка питомца для редактирования

- В `PetsModule.editPet(petId)`:

```203:238:web/static/js/pets.js
async editPet(petId) {
    const response = await fetch(`/api/pets/${petId}`, { credentials: 'include' });
    const data = await response.json();
    const pet = data.pet;

    document.getElementById('pet-record-id').value = pet._id;
    document.getElementById('pet-name').value = pet.name || '';
    document.getElementById('pet-breed').value = pet.breed || '';
    document.getElementById('pet-birth-date').value = pet.birth_date || '';
    document.getElementById('pet-gender').value = pet.gender || '';
    document.getElementById('pet-form-title').textContent = 'Редактировать питомца';
    document.getElementById('pet-submit-btn').textContent = 'Обновить';

    // Фото
    const photoCurrent = document.getElementById('pet-photo-current');
    const photoCurrentImg = document.getElementById('pet-photo-current-img');
    if (pet.photo_url) {
        photoCurrentImg.src = pet.photo_url + '?t=' + new Date().getTime();
        photoCurrent.style.display = 'block';
    } else {
        photoCurrent.style.display = 'none';
    }

    const accessSection = document.getElementById('pet-access-section');
    if (pet.current_user_is_owner) {
        accessSection.style.display = 'block';
        await this.loadPetAccessInForm(petId);
    } else {
        accessSection.style.display = 'none';
    }

    if (typeof showScreen === 'function') {
        showScreen('pet-form');
    }
}
```

#### Список пользователей с доступом (внутри `pet-form`)

- `PetsModule.loadPetAccessInForm(petId)`:

```247:273:web/static/js/pets.js
const response = await fetch(`/api/pets/${petId}`, { credentials: 'include' });
const data = await response.json();
const pet = data.pet;
const sharedWith = pet.shared_with || [];
// Если пусто — выводим empty-state
// Иначе — рендерим .shared-users-list с кнопкой «Убрать доступ»
```

- Удаление доступа:
  - Кнопки вызывают `PetsModule.unsharePetFromForm(petId, username)`, которая бьёт по `DELETE /api/pets/<pet_id>/share/<username>`.

#### Создание/обновление питомца

- Обработчик отправки формы:

```746:787:web/templates/dashboard.html
document.getElementById('pet-form-element').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const recordId = formData.get('pet_id');

    const url = recordId ? `/api/pets/${recordId}` : '/api/pets';
    const method = recordId ? 'PUT' : 'POST';

    const response = await fetch(url, {
        method: method,
        credentials: 'include',
        body: formData
    });
    const result = await response.json();
    if (response.ok) {
        showAlert('success', result.message || (recordId ? 'Питомец обновлен' : 'Питомец создан'));
        resetPetForm();
        if (!recordId && result.pet) {
            setSelectedPet(result.pet._id, result.pet.name);
        }
        await renderPetsList();
        setTimeout(() => { showScreen('pet-selector'); }, 150);
    } else {
        showAlert('error', result.error || 'Ошибка при сохранении');
    }
});
```

- Обработка файла фото и флага `remove_photo`:

```710:744:web/templates/dashboard.html
document.getElementById('pet-photo-file').addEventListener('change', ...);
function clearPetPhoto() {
    document.getElementById('pet-photo-file').value = '';
    document.getElementById('pet-photo-preview').style.display = 'none';
    // Mark photo for removal
    const form = document.getElementById('pet-form-element');
    const removeInput = document.createElement('input');
    removeInput.type = 'hidden';
    removeInput.name = 'remove_photo';
    removeInput.value = 'true';
    form.appendChild(removeInput);
}
```

- Бэкенд ожидает `multipart/form-data` и обрабатывает `remove_photo` в `/api/pets/<pet_id>` (см. `update_pet` в `app.py`).

#### Сброс формы питомца

- `PetsModule.resetPetForm()`:

```361:379:web/static/js/pets.js
resetPetForm() {
    document.getElementById('pet-form-element').reset();
    document.getElementById('pet-record-id').value = '';
    document.getElementById('pet-form-title').textContent = 'Добавить питомца';
    document.getElementById('pet-submit-btn').textContent = 'Сохранить';
    // Скрытие превью фото и секции доступа
}
```

Глобальная обёртка `resetPetForm()` используется:

- из `pet-selector` при нажатии «+ Добавить питомца»,
- после успешного сохранения.

### API и права доступа (бекенд)

Основные эндпоинты в [`web/app.py`](web/app.py):

- Список питомцев:
  - `GET /api/pets` — использует `check_pet_access`, возвращает только доступные пользователю питомцы.
- Создание питомца:
  - `POST /api/pets` — доступно авторизованным пользователям, новые питомцы становятся их `owner`.
- Получение/обновление/удаление:
  - `GET /api/pets/<pet_id>` — доступно владельцу и пользователям из `shared_with`.
  - `PUT /api/pets/<pet_id>`, `DELETE /api/pets/<pet_id>` — только для владельца (`require_owner=True`).
- Доступ (sharing) описан подробно в документе `pet-sharing.md`.

### Инварианты для рефакторинга

1. **ID/имена полей `pet-form`**:
   - `id="pet-form-element"`, скрытое `name="pet_id"` (`#pet-record-id`),
   - `name="name"`, `name="breed"`, `name="birth_date"`, `name="gender"`, `name="photo_file"`,
   - `#pet-photo-preview`, `#pet-photo-preview-img`, `#pet-photo-current`, `#pet-photo-current-img`,
   - `#pet-access-section`, `#pet-shared-with-list`, `#share-username-input`.
2. **Сигнатуры функций `PetsModule`**:
   - `init`, `renderPetsList`, `selectPet`, `editPet`, `loadPetAccessInForm`, `sharePetFromForm`,
     `unsharePetFromForm`, `showPetSharing`, `resetPetForm` должны быть либо сохранены, либо адаптированы
     вместе с вызывающим их кодом (`dashboard.html`, `pet-sharing`).
3. **Навигация**:
   - Pереходы `showScreen('pet-selector')` и `showScreen('pet-form')` должны продолжать работать,
     даже если будет изменена разметка (например, при переходе на чистые F7‑формы).


