# csrf-lab

Учебный полигон для демонстрации CSRF-атак и защиты от них через
[csrf-shield](https://github.com/m2xdev/csrf-shield) (Double Submit Cookie + HMAC-SHA256).

## Что это

Flask-приложение с симуляцией банковского перевода: уязвимая версия и защищённая
версия рядом, плюс страница «атакующего» с поддельной формой — чтобы наглядно
показать, как работает CSRF-атака и как её блокирует `csrf-shield`.

| Маршрут | Что показывает |
|---|---|
| `/` | Главная страница, список пользователей |
| `/bank` | Баланс текущего пользователя |
| `/transfer_vulnerable` | Перевод денег без CSRF-защиты |
| `/transfer_protected` | Тот же перевод, но с проверкой через `csrf-shield` |
| `/attacker` | Страница «злоумышленника» с поддельной формой перевода |

## Установка и запуск

```bash
git clone https://github.com/m2xdev/csrf-lab
cd csrf-lab
pip install -r requirements.txt
python app.py
```

Открыть в браузере: `http://127.0.0.1:5000`

## Как попробовать атаку

1. Открой `http://127.0.0.1:5000/bank` — посмотри текущий баланс `alice`.
2. Открой `http://127.0.0.1:5000/attacker` в **новой вкладке** — это имитация
   стороннего сайта, на который могла бы попасть жертва.
3. Нажми кнопку на странице атакующего — она отправит скрытый перевод
   на `/transfer_vulnerable` от имени `alice`, без её ведома.
4. Вернись на `/bank` — баланс изменился, хотя ты ничего не подтверждал.
5. Повтори то же самое, но для `/transfer_protected` — увидишь, что запрос
   будет отклонён (`403: CSRF: Token mismatch` или `Missing token`),
   потому что у страницы атакующего нет доступа к настоящему CSRF-токену.

## ⚠️ Дисклеймер / Disclaimer

### Русская версия

Этот репозиторий содержит **намеренно уязвимый код** (`/transfer_vulnerable`,
`/attacker`) и предназначен исключительно для обучения и демонстрации
механизмов CSRF-атак и защиты от них.

- Запускайте только локально или в изолированной среде (Docker/VM), никогда —
  на публичном сервере или в общей сети.
- Не используйте код из `/transfer_vulnerable` как образец для реальных
  проектов — это намеренный антипример.
- Не тестируйте техники, показанные здесь, на чужих сайтах или системах без
  явного разрешения — это может быть незаконно.
- Баланс и пользователи хранятся только в памяти процесса и сбрасываются
  при каждом перезапуске — это не настоящая база данных.

Программное обеспечение предоставляется **«КАК ЕСТЬ»**, без каких-либо
явных или подразумеваемых гарантий. Используя данный код, вы самостоятельно
несёте ответственность за его применение и любые последствия. Автор не несёт
ответственности за ущерб, возникший в результате использования данного ПО.

### English version

This repository contains **intentionally vulnerable code**
(`/transfer_vulnerable`, `/attacker`) and is intended solely for educational
purposes — to demonstrate CSRF attack and defense mechanisms.

- Run locally or in an isolated environment (Docker/VM) only — never on a
  public server or shared network.
- Do not use the code in `/transfer_vulnerable` as a template for real
  projects — it is a deliberate anti-pattern.
- Do not test the techniques shown here against third-party sites or systems
  without explicit authorization — doing so may be illegal.
- Balances and users are stored in memory only and reset on every restart —
  this is not a real database.

The software is provided **"AS IS"**, without warranty of any kind, express
or implied. By using this code, you are solely responsible for its use and
any resulting consequences. The author is not liable for any damages arising
from the use of this software.

## Связанные проекты

- [csrf-shield](https://github.com/m2xdev/csrf-shield) — сама библиотека защиты
- [xss-shield](https://github.com/m2xdev/xss-shield) — защита от XSS (nh3)
- [xss-lab](https://github.com/m2xdev/xss-lab) — учебный полигон для XSS
- [query-sql](https://github.com/m2xdev/query-sql) — защита от SQL-инъекций
- [query-lab](https://github.com/m2xdev/query-lab) — учебный полигон для SQL-инъекций