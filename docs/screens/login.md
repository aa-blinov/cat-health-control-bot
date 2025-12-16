## Экран `login` — вход в систему

### Назначение

Экран логина позволяет пользователю ввести имя пользователя и пароль, после чего:

- фронтенд отправляет форму на `/login` (HTML‑поток),
- бэкенд проверяет креды и выставляет JWT‑токены в httpOnly‑cookies,
- при успехе пользователь перенаправляется на `/dashboard`.

Также есть чистый API‑логин (`/api/auth/login`), который используется не этим шаблоном,
но логика проверок совпадает.

---

## Разметка

Файл [`web/templates/login.html`](web/templates/login.html):

```8:25:web/templates/login.html
<div class="login-container">
    <div class="login-card">
        <h2>Вход в систему</h2>
        {% if error %}
        <div class="alert alert-error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="{{ url_for('login') }}"
              class="login-form" enctype="application/x-www-form-urlencoded">
            <div class="form-group">
                <label for="username">Логин:</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label for="password">Пароль:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Войти</button>
        </form>
    </div>
</div>
```

Ключевые элементы:

- `#username`, `#password` — поля логина/пароля.
- Сообщение об ошибке — блок `.alert.alert-error` при наличии переменной `error` в контексте шаблона.

Стили (`web/static/css/style.css`):

- `.login-container`, `.login-card`, `.login-form` задают выравнивание по центру, отступы и тёмную тему.

---

## Бэкенд‑логика `/login`

Реализована в [`web/app.py`](web/app.py):

```658:728:web/app.py
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("50 per 5 minutes", error_message="Слишком много попыток. Попробуйте позже.")
def login():
    # Если уже залогинен — редирект на dashboard
    token = get_token_from_request()
    if token:
        payload = verify_token(token, "access")
        if payload:
            return redirect(url_for("dashboard"))

    # Попытка обновить токен по refresh_token
    new_token = try_refresh_access_token()
    if new_token:
        ...
        return response

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        client_ip = request.remote_addr

        if not username or not password:
            return render_template("login.html", error="Введите логин и пароль")

        if verify_user_credentials(username, password):
            access_token = create_access_token(username)
            refresh_token = create_refresh_token(username)
            # логирование, выставление cookies, редирект на dashboard
        else:
            # неверные креды
            return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")
```

### Детали

- Проверка учётных данных:
  - `verify_user_credentials(username, password)` сначала ищет пользователя в коллекции `users`,
    затем, при необходимости, делает fallback к `ADMIN_USERNAME/ADMIN_PASSWORD_HASH`.
- При успешном логине:
  - создаются `access_token` и `refresh_token` (JWT),
  - оба помещаются в httpOnly‑cookies (`access_token`, `refresh_token`),
  - пользователь переадресуется на `/dashboard`.
- При ошибочном логине:
  - логируется предупреждение,
  - тот же шаблон `login.html` рендерится с параметром `error`.

---

## API‑логин `/api/auth/login` (для полноты картины)

Хотя экран `login` им не пользуется, поведение важно для согласованности:

- Эндпоинт: `POST /api/auth/login`
- Тело JSON: `{ "username": "...", "password": "..." }`.
- При успехе:
  - возвращает `{ success: true, access_token, refresh_token, ... }`,
  - выставляет те же cookies, что и HTML‑логин.

---

## Навигация и переходы

- Стартовый роут `/`:
  - если есть валидный `access_token` (или удаётся освежить по `refresh_token`) — редирект на `/dashboard`,
  - иначе — редирект на `/login`.
- Роут `/logout`:
  - вызывает `api_logout()` для очистки токенов и базы refresh‑токенов,
  - редиректит на `/login`.

---

## Инварианты для рефакторинга

1. **Имена полей формы**: `name="username"` и `name="password"` должны сохраняться, чтобы
   существующая логика `/login` продолжала работать.
2. **URL формы**: `action="{{ url_for('login') }}"` (или эквивалент `/login`) — изменять только при
   смене серверной логики.
3. **Отображение ошибок**: шаблон должен по‑прежнему учитывать переменную `error` и показывать её
   пользователю, чтобы не ломать UX при ошибках входа.


