## Админ‑панель: `admin-panel` и форма пользователя `user-form`

### Назначение

Эти экраны доступны только администраторам и позволяют:

- просматривать список пользователей,
- создавать новых пользователей,
- редактировать профиль (ФИО, email, статус),
- активировать/деактивировать пользователя,
- сбрасывать пароли.

### Отображение ссылки на админ‑панель

- В главном меню:

```40:43:web/templates/dashboard.html
<div class="card action-card action-card-admin admin-link"
     onclick="showScreen('admin-panel')" style="display: none;">
    <h3>Админ-панель</h3>
    <p>Управление пользователями</p>
</div>
```

- Видимость управляется модулем `UsersModule.checkAdminStatus()` (см. `users.js` и `/api/users` в бэкенде).

---

## Экран `admin-panel`

### Разметка

- Контейнер:

```247:262:web/templates/dashboard.html
<div id="admin-panel" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('main-menu')">← Назад</button>
        <h2>Админ-панель</h2>
    </div>
    <div class="admin-content">
        <div class="admin-section">
            <h3>Пользователи</h3>
            <button class="btn btn-primary btn-block"
                    onclick="resetUserForm(); showScreen('user-form');">+ Добавить пользователя</button>
            <div id="users-list" class="users-list">
                <div class="loading">Загрузка...</div>
            </div>
        </div>
    </div>
</div>
```

- Список пользователей (`#users-list`) наполняется `UsersModule.loadUsersList()` таблицей для десктопа и карточками для мобильных.

### JS‑логика: `UsersModule`

Файл [`web/static/js/users.js`](web/static/js/users.js):

#### Проверка прав администратора

```5:34:web/static/js/users.js
async checkAdminStatus() {
    try {
        const response = await fetch('/api/users', { credentials: 'include' });
        this.isAdmin = response.ok;
        const adminLink = document.querySelector('.admin-link');
        if (adminLink) {
            adminLink.style.display = this.isAdmin ? 'flex' : 'none';
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

#### Загрузка списка пользователей

```36:128:web/static/js/users.js
async loadUsersList() {
    const container = document.getElementById('users-list');
    container.innerHTML = '<div class="loading">Загрузка...</div>';

    const response = await fetch('/api/users', { credentials: 'include' });
    // ... обработка ошибок ...
    const data = await response.json();
    const users = data.users || [];

    // Desktop-таблица .users-table
    // ...
    // Мобильные карточки .users-cards
}
```

- Табличный вид (десктоп):
  - Колонки: имя пользователя, полное имя, email, статус, действия.
  - Действия:
    - `Редактировать` → `UsersModule.editUser(username)`.
    - `Сбросить пароль` → `UsersModule.resetUserPassword(username)` (кроме `admin`).
    - `Деактивировать` / `Активировать` → `UsersModule.deactivateUser/activateUser`.

- Мобильный вид:
  - Карточки `user-card` с аналогичным набором действий, но кнопки `btn btn-* btn-block`.

#### Работа с формой пользователя

- Сброс формы:

```134:146:web/static/js/users.js
resetUserForm() {
    document.getElementById('user-record-username').value = '';
    document.getElementById('user-form-element').reset();
    document.getElementById('user-username').value = '';
    document.getElementById('user-username').disabled = false;
    document.getElementById('user-password').value = '';
    document.getElementById('user-password').required = true;
    document.getElementById('user-password-label').textContent = 'Пароль *';
    document.getElementById('user-full-name').value = '';
    document.getElementById('user-email').value = '';
    document.getElementById('user-form-title').textContent = 'Добавить пользователя';
    document.getElementById('user-submit-btn').textContent = 'Сохранить';
}
```

- Редактирование пользователя:

```148:169:web/static/js/users.js
async editUser(username) {
    const response = await fetch(`/api/users/${username}`, { credentials: 'include' });
    const data = await response.json();
    const user = data.user;

    document.getElementById('user-record-username').value = user.username;
    document.getElementById('user-username').value = user.username;
    document.getElementById('user-username').disabled = true;
    document.getElementById('user-password').value = '';
    document.getElementById('user-password').required = false;
    document.getElementById('user-password-label').textContent =
        'Пароль (оставьте пустым, чтобы не менять)';
    document.getElementById('user-full-name').value = user.full_name || '';
    document.getElementById('user-email').value = user.email || '';
    document.getElementById('user-form-title').textContent = 'Редактировать пользователя';
    document.getElementById('user-submit-btn').textContent = 'Обновить';

    showScreen('user-form');
}
```

### Экран `user-form`

### Разметка

```265:292:web/templates/dashboard.html
<div id="user-form" class="screen">
    <div class="form-header">
        <button class="back-btn" onclick="showScreen('admin-panel')">← Назад</button>
        <h2 id="user-form-title">Добавить пользователя</h2>
    </div>
    <form id="user-form-element" class="inline-form">
        <input type="hidden" id="user-record-username" name="username" value="">
        <div class="form-group">
            <label for="user-username">Имя пользователя *</label>
            <input type="text" id="user-username" name="username" required placeholder="user123">
        </div>
        <div class="form-group">
            <label for="user-password" id="user-password-label">Пароль *</label>
            <input type="password" id="user-password" name="password" required placeholder="Введите пароль">
        </div>
        <div class="form-group">
            <label for="user-full-name">Полное имя</label>
            <input type="text" id="user-full-name" name="full_name" placeholder="Мария Иванова">
        </div>
        <div class="form-group">
            <label for="user-email">Email</label>
            <input type="email" id="user-email" name="email" placeholder="email@example.com">
        </div>
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-block" id="user-submit-btn">Сохранить</button>
            <button type="button" class="btn btn-secondary btn-block" onclick="showScreen('admin-panel')">Отмена</button>
        </div>
    </form>
</div>
```

### Обработчик отправки формы пользователя

В `dashboard.html`:

```474:566:web/templates/dashboard.html
const userForm = document.getElementById('user-form-element');
if (userForm) {
    userForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const recordUsername = formData.get('username'); // из hidden
        const username = document.getElementById('user-username').value;
        const password = formData.get('password');
        const data = {
            username: username,
            full_name: formData.get('full_name') || '',
            email: formData.get('email') || ''
        };

        if (recordUsername) {
            // режим обновления
            if (password) {
                // отдельный запрос для смены пароля
                await fetch(`/api/users/${username}/reset-password`, { ... });
            }
            await fetch(`/api/users/${username}`, {
                method: 'PUT', headers: {'Content-Type': 'application/json'},
                credentials: 'include', body: JSON.stringify(data)
            });
            // при успехе: showAlert, resetUserForm, возврат на admin-panel, loadUsersList
        } else {
            // режим создания
            if (!password) {
                showAlert('error', 'Пароль обязателен для нового пользователя');
                return;
            }
            data.password = password;
            await fetch('/api/users', { method: 'POST', ... });
            // аналогично: showAlert, resetUserForm, возврат на admin-panel
        }
    });
}
```

Здесь deliberately используется отдельный API для смены пароля (`reset-password`),
чтобы не смешивать изменение профиля и пароля в одном запросе.

### Управление паролем и статусом

- Сброс пароля:

```178:205:web/static/js/users.js
async resetUserPassword(username) {
    const newPassword = prompt('Введите новый пароль:');
    if (!newPassword) return;
    const response = await fetch(`/api/users/${username}/reset-password`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({password: newPassword})
    });
    // showAlert по результату
}
```

- Деактивация/активация:

```207:265:web/static/js/users.js
async deactivateUser(username) {
    if (!confirm(...)) return;
    await fetch(`/api/users/${username}`, { method: 'DELETE', credentials: 'include' });
    // ... showAlert, reload list ...
}

async activateUser(username) {
    if (!confirm(...)) return;
    await fetch(`/api/users/${username}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({is_active: true})
    });
}
```

### API и права доступа

Все админ‑эндпоинты в [`web/app.py`](web/app.py) защищены двумя декораторами:

- `@login_required` — проверка JWT/refresh токенов,
- `@admin_required` — проверка, что `request.current_user` — администратор.

Основные маршруты:

- `GET /api/users` — список всех пользователей.
- `POST /api/users` — создание пользователя.
- `GET /api/users/<username>` — данные по одному пользователю.
- `PUT /api/users/<username>` — обновление профиля (`full_name`, `email`, `is_active`).
- `DELETE /api/users/<username>` — деактивация пользователя.
- `POST /api/users/<username>/reset-password` — смена пароля.

### Инварианты для рефакторинга

1. **ID/имена полей формы пользователя**:
   - `#user-form-element`, `#user-record-username`, `#user-username`, `#user-password`,
     `#user-full-name`, `#user-email`, `#user-password-label`, `#user-form-title`, `#user-submit-btn`.
2. **Классы и ID для списка пользователей**:
   - `#users-list` и внутренняя структура (`.users-table`, `.users-cards`, `.table-actions`, `.user-card-actions`)
     используются только на фронте; при смене разметки важно сохранить функциональные связи с `UsersModule.*`.
3. **Навигация**:
   - `showScreen('admin-panel')` и `showScreen('user-form')` должны оставаться валидными ID экранов.
4. **Разделение операций**:
   - Обновление профиля и смена пароля разнесены по разным API; новый UI не должен объединять их без
     синхронизации с бэкендом.


