# Bookstore API — автентифікація і захист

> Цей файл — **шаблон вашого звіту**. Заповніть розділи нижче і закомітьте разом із кодом.
> Умова завдання — у Moodle.

## Варіант

- Номер варіанта: **1**
- Схема: Token
- Право: P1
- Throttle: 5 запитів/год для аноніма · 100 запитів/добу для користувача
- Інтеграція: I1
- Відеозахист (до 3 хв): - 

## Запуск

```bash
python3 -m venv venv              # Windows: py -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed             # автори, 30 книг, користувачі й групи
python manage.py runserver
python manage.py test
```

Тестові користувачі (`python manage.py seed`), пароль `pass12345`:

| Користувач | Пошта | Акаунт | Група / роль |
|---|---|---|---|
| alice | alice@kpi.edu.ua | 30 днів | Editors, власниця третини книг |
| bob | bob@lnu.edu.ua | 30 днів | Editors |
| carol | carol@gmail.com | 30 днів | — |
| newbie | newbie@kpi.edu.ua | щойно | Editors |
| moder | moder@gmail.com | 30 днів | Moderators |
| staff | staff@gmail.com | 30 днів | `is_staff` |
| admin | admin@example.com | — | суперкористувач, пароль `admin` |

## Результат тестів

Вставте останні рядки `python manage.py test`:

```
Ran 59 tests in 52.127s

OK (skipped=35)
Destroying test database for alias 'default'...
```

## Журнал `curl -i`

Для кожного пункту — команда і **перші рядки** відповіді (статус і важливі заголовки).

### 1. Вхід і вихід

Вхід:

```
curl.exe -i -X POST http://127.0.0.1:8000/api/v1/auth/token/ -d "username=alice&password=pass12345"

HTTP/1.1 200 OK
Content-Type: application/json
Allow: POST, OPTIONS

{"token":"f06079f77c71821069aadc2a8596c09dcb602e19"}
```

Вихід і повторний запит з тим самим ключем:

```
ВСТАВТЕ: 204 No Content, потім 401 з WWW-Authenticate: Token
```

### 2. Право доступу: дозволено і заборонено

```
ВСТАВТЕ: alice (@kpi.edu.ua) → 201; carol (@gmail.com) → 403; анонім → 401
```

### 3. Throttling: останній дозволений запит і `429`

```
ВСТАВТЕ: 5-й запит до /api/v1/authors/ → 200; 6-й → 429 (і рядок Retry-After)
```

### 4. Інтеграційна вимога (I1)

```
ВСТАВТЕ: GET /api/v1/books/1/ (author — об'єкт, owner — рядок); POST з author_id=999999 → 400
```


## Журнал помилок

Щонайменше дві помилки, на які ви справді натрапили.

| Що побачили (текст помилки або код) | Причина | Що змінили |
|---|---|---|
| `AssertionError: 'bookstore.permissions' not found in ['rest_framework.permissions']`, `FAILED (failures=6)` після першого коміту | Тести анонімного доступу (401 замість 200, заголовок `WWW-Authenticate`, префікс `Bearer`) і перевірка власного класу прав запускались, поки в `BookViewSet` ще не було власного права: діяв стандартний `AllowAny` | Додав `IsEduUserOrReadOnly` і підключив його в `permission_classes`; після цього `test_scheme`, `test_permissions`, `test_baseline` дали `OK`; на першому кроці надалі запускав лише тести входу й виходу |

| | | |

## Дослідницькі питання

1. **Де зберігаються токени.** У таблиці `authtoken_token` бази даних (модель `rest_framework.authtoken.models.Token`: ключ, користувач, дата створення). Якщо видалити рядок у `manage.py shell` (`Token.objects.filter(user__username="alice").delete()`), цей ключ одразу перестає працювати і дає 401. Новий ключ видається при наступному вході. Джерело: документація DRF, Authentication; `rest_framework/authtoken/models.py`.
2. **Throttle у `ObtainAuthToken`.** У цього класу `throttle_classes = ()`, тобто порожній кортеж, тому глобальні ліміти на `/auth/token/` не діють і паролі можна перебирати без обмежень. Виправлення: у власному підкласі задати `throttle_classes`. У мене це `LoginRateThrottle` зі scope `login` і ліміт `10/min`. Джерело: `rest_framework/authtoken/views.py`.
3. **Чому токену не потрібен CSRF.** CSRF-атака працює, бо браузер сам додає cookie сесії до міжсайтового запиту. Токен лежить не в cookie, а в заголовку `Authorization`, який клієнт додає вручну, і чужий сайт не може змусити браузер його надіслати. Тому `SessionAuthentication` у DRF перевіряє CSRF, а `TokenAuthentication` ні. Джерело: документація DRF, Authentication.
4. **Порядок перевірок у `APIView.initial()`.** Спочатку content negotiation і версія, потім `perform_authentication`, `check_permissions` і `check_throttles`. Анонімний `POST /books/` отримує 401 на `check_permissions` і до `check_throttles` не доходить, тому не витрачає ліміт аноніма. Анонімний `GET /authors/` проходить права (`AllowAny`), потрапляє в `check_throttles` і списує ліміт: на 6-му запиті за годину буде 429. Джерело: `rest_framework/views.py`, метод `initial`.


## Якщо користувались ШІ

Що саме питали і що з відповіді виявилось неправильним або не підійшло до вашого коду.
Якщо не користувались — так і напишіть.

