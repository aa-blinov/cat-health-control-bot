## Доступ к питомцу: экран `pet-sharing` и блок доступа в `pet-form`

### Назначение

Механизм шаринга позволяет владельцу питомца:

- предоставлять доступ другим пользователям (с возможностью читать/вводить записи по питомцу),
- отзывать доступ,
- просматривать список пользователей, имеющих доступ.

Пользователь, которому предоставлен доступ, видит питомца в списке и может работать с его данными,
но не видит административных функций по шерингу (если он не владелец).

---

## Блок доступа внутри `pet-form`

### Разметка

Внутри формы питомца (`#pet-form-element`):

```223:237:web/templates/dashboard.html
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
```

- Секция показывается только если текущий пользователь — владелец питомца.

### JS‑логика внутри `PetsModule`

#### Показ секции доступа при редактировании питомца

```228:234:web/static/js/pets.js
const accessSection = document.getElementById('pet-access-section');
if (pet.current_user_is_owner) {
    accessSection.style.display = 'block';
    await this.loadPetAccessInForm(petId);
} else {
    accessSection.style.display = 'none';
}
```

#### Загрузка списка пользователей с доступом

```247:273:web/static/js/pets.js
async loadPetAccessInForm(petId) {
    const response = await fetch(`/api/pets/${petId}`, { credentials: 'include' });
    const data = await response.json();
    const pet = data.pet;

    const sharedList = document.getElementById('pet-shared-with-list');
    const sharedWith = pet.shared_with || [];
    if (sharedWith.length === 0) {
        sharedList.innerHTML = '<div class="empty-state"><p>Нет пользователей с доступом</p></div>';
    } else {
        let html = '<div class="shared-users-list">';
        sharedWith.forEach(username => {
            html += `
                <div class="shared-user-item">
                    <div class="shared-user-name">${username}</div>
                    <div class="shared-user-actions">
                        <button class="btn btn-secondary btn-block"
                                onclick="PetsModule.unsharePetFromForm('${petId}', '${username}')">
                            Убрать доступ
                        </button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        sharedList.innerHTML = html;
    }
}
```

#### Предоставление доступа из `pet-form`

```279:323:web/static/js/pets.js
async sharePetFromForm() {
    const petId = document.getElementById('pet-record-id').value;
    const usernameInput = document.getElementById('share-username-input');
    const username = usernameInput.value.trim();

    if (!username) {
        showAlert('error', 'Введите имя пользователя');
        return;
    }
    if (!petId) {
        showAlert('error', 'Сначала сохраните питомца');
        return;
    }

    const response = await fetch(`/api/pets/${petId}/share`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({username: username})
    });
    const result = await response.json();
    if (response.ok) {
        showAlert('success', result.message || 'Доступ предоставлен');
        usernameInput.value = '';
        await this.loadPetAccessInForm(petId);
    } else {
        showAlert('error', result.error || 'Ошибка при предоставлении доступа');
    }
}
```

#### Отзыв доступа из `pet-form`

```325:352:web/static/js/pets.js
async unsharePetFromForm(petId, username) {
    if (!confirm(`Убрать доступ у пользователя ${username}?`)) return;
    const response = await fetch(`/api/pets/${petId}/share/${username}`, {
        method: 'DELETE',
        credentials: 'include'
    });
    const result = await response.json();
    if (response.ok) {
        showAlert('success', result.message || 'Доступ убран');
        await this.loadPetAccessInForm(petId);
    } else {
        showAlert('error', result.error || 'Ошибка при удалении доступа');
    }
}
```

---

## Экран `pet-sharing`

### Разметка

```295:327:web/templates/dashboard.html
<div id="pet-sharing" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('pet-selector')">← Назад</button>
        <h2>Доступ к животному</h2>
    </div>
    <div class="sharing-content">
        <div id="sharing-info" class="sharing-section">
            <h3>Пользователи с доступом</h3>
            <div id="shared-with-list" class="shared-list">
                <div class="loading">Загрузка...</div>
            </div>
        </div>

        <div id="sharing-owner-section" class="sharing-section" style="display: none;">
            <h3>Поделиться с пользователем</h3>
            <form id="share-form" class="inline-form">
                <div class="form-group">
                    <label for="share-username">Имя пользователя</label>
                    <input type="text" id="share-username" name="username" required placeholder="Введите имя пользователя">
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary btn-block">Поделиться</button>
                </div>
            </form>
        </div>

        <div id="sharing-user-section" class="sharing-section" style="display: none;">
            <div class="empty-state">
                <p>У вас нет доступа к этому животному</p>
            </div>
        </div>
    </div>
</div>
```

### JS‑логика: функции в `dashboard.html`

#### Загрузка информации о доступе

```678:713:web/templates/dashboard.html
async function loadPetSharing() {
    const petId = getSelectedPetId();
    if (!petId) {
        showAlert('error', 'Выберите животное');
        return;
    }

    const response = await fetch(`/api/pets/${petId}`, { credentials: 'include' });
    if (!response.ok) {
        showAlert('error', 'Ошибка загрузки информации о питомце');
        return;
    }
    const data = await response.json();
    const pet = data.pet;

    const userIsOwner = pet.current_user_is_owner || false;
    const sharedWith = pet.shared_with || [];
    const hasAccess = userIsOwner || sharedWith.length >= 0; // всегда true, если дошли до экрана

    document.getElementById('sharing-owner-section').style.display = userIsOwner ? 'block' : 'none';
    document.getElementById('sharing-user-section').style.display = hasAccess ? 'none' : 'block';

    if (hasAccess) {
        await loadSharedWithList(pet);
    }
}
```

#### Отрисовка списка пользователей с доступом (экран `pet-sharing`)

```720:742:web/templates/dashboard.html
async function loadSharedWithList(pet) {
    const container = document.getElementById('shared-with-list');
    const sharedWith = pet.shared_with || [];
    if (sharedWith.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Нет пользователей с доступом</p></div>';
        return;
    }
    let html = '<div class="shared-users-list">';
    sharedWith.forEach(username => {
        html += `
            <div class="shared-user-item">
                <div class="shared-user-name">${username}</div>
                ${pet.current_user_is_owner ? `
                <div class="shared-user-actions">
                    <button class="btn btn-secondary btn-block" onclick="unsharePet('${username}')">Убрать доступ</button>
                </div>
                ` : ''}
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}
```

#### Предоставление доступа (экран `pet-sharing`)

```803:814:web/templates/dashboard.html
document.getElementById('share-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const username = formData.get('username').trim();

    if (!username) {
        showAlert('error', 'Введите имя пользователя');
        return;
    }

    await sharePetWithUser(username);
});
```

- `sharePetWithUser(username)`:

```746:770:web/templates/dashboard.html
async function sharePetWithUser(username) {
    const petId = getSelectedPetId();
    if (!petId) {
        showAlert('error', 'Выберите животное в меню навигации');
        return;
    }
    const response = await fetch(`/api/pets/${petId}/share`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({username: username})
    });
    const result = await response.json();
    if (response.ok) {
        showAlert('success', result.message || 'Доступ предоставлен');
        document.getElementById('share-form').reset();
        loadPetSharing();
    } else {
        showAlert('error', result.error || 'Ошибка при предоставлении доступа');
    }
}
```

#### Отзыв доступа (экран `pet-sharing`)

```774:799:web/templates/dashboard.html
async function unsharePet(username) {
    const petId = getSelectedPetId();
    if (!petId) return;

    if (!confirm(`Убрать доступ у пользователя ${username}?`)) return;

    const response = await fetch(`/api/pets/${petId}/share/${username}`, {
        method: 'DELETE',
        credentials: 'include'
    });
    const result = await response.json();
    if (response.ok) {
        showAlert('success', result.message || 'Доступ убран');
        loadPetSharing();
    } else {
        showAlert('error', result.error || 'Ошибка при удалении доступа');
    }
}
```

### Вход в экран `pet-sharing`

- Через список питомцев:

```354:359:web/static/js/pets.js
showPetSharing(petId, petName) {
    this.setSelectedPet(petId, petName);
    if (typeof loadPetSharing === 'function') {
        loadPetSharing();
    }
}
```

- `pet-selector` вызывает `PetsModule.showPetSharing(pet._id, pet.name)` по кнопке «Доступ».

- Навигация:
  - `showScreen('pet-sharing')` вызывается в `NavigationModule.showScreen`, когда переходим на этот экран,
    и внутри него вызывается `loadPetSharing()`:

```66:69:web/static/js/navigation.js
} else if (screenId === 'pet-sharing') {
    if (typeof loadPetSharing === 'function') {
        loadPetSharing();
    }
}
```

---

## Бэкенд: API и правила доступа

Все операции шаринга реализованы в [`web/app.py`](web/app.py).

### Предоставление доступа

- `POST /api/pets/<pet_id>/share`:
  - Доступно только владельцу (`require_owner=True`).
  - Тело: `{ "username": "<имя пользователя>" }`.
  - Проверяет:
    - что пользователь существует и активен,
    - что нельзя шарить самому себе,
    - что доступ ещё не был предоставлен.
  - Добавляет `username` в массив `shared_with` документа питомца.

### Отзыв доступа

- `DELETE /api/pets/<pet_id>/share/<share_username>`:
  - Доступно только владельцу.
  - Удаляет `share_username` из `shared_with`.

### Общие проверки доступа

- Помощники:
  - `validate_pet_id`, `check_pet_access`, `get_pet_and_validate` в `app.py`.
  - `get_pet_and_validate(..., require_owner=True)` используется для всех операций, где требуется
    именно владелец.

### Инварианты для рефакторинга

1. **ID элементов и структура DOM**:
   - `#pet-access-section`, `#pet-shared-with-list`, `#share-username-input` в `pet-form`,
   - `#pet-sharing`, `#shared-with-list`, `#sharing-owner-section`, `#sharing-user-section`,
     `#share-form`, `#share-username` в экране `pet-sharing`.
2. **Функции и точки входа**:
   - `loadPetSharing`, `loadSharedWithList`, `sharePetWithUser`, `unsharePet`,
     `PetsModule.showPetSharing`, `PetsModule.sharePetFromForm`, `PetsModule.unsharePetFromForm`.
3. **Правила прав доступа**:
   - Владельцы видят и могут использовать блоки «Поделиться» / «Убрать доступ».
   - Пользователи с доступом видят только список и сам питомец появляется у них в списке питомцев.


