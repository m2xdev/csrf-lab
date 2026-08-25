# app.py
# CSRF-LAB — лаборатория для изучения CSRF-атак

from flask import Flask, render_template, request, session, redirect, url_for, abort
import secrets
import hmac

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# =========================================================
# ПОДКЛЮЧАЕМ CSRF-ЗАЩИТУ (БЕЗ ГЛОБАЛЬНОГО before_request)
# =========================================================
from csrf_shield import CSRFShield, CSRFConfig, CSRFToken

csrf = CSRFShield(config=CSRFConfig())
csrf.secret_key = app.secret_key  # Выставляем вручную

# Регистрируем контекстный процессор для шаблонов
@app.context_processor
def inject_csrf():
    return {'csrf_token': csrf.get_token}

# Устанавливаем CSRF-куку после каждого запроса
@app.after_request
def set_csrf_cookie(response):
    return csrf._after_request(response)

# =========================================================
# БАНКОВСКАЯ СИМУЛЯЦИЯ (ХРАНИЛИЩЕ В ПАМЯТИ)
# =========================================================
users = {
    'alice': {'balance': 5000, 'password': 'alice123'},
    'bob': {'balance': 1000, 'password': 'bob123'},
    'eve': {'balance': 100, 'password': 'eve123'},
}

current_user = 'alice'  # По умолчанию залогинена Алиса

# =========================================================
# ГЛАВНАЯ СТРАНИЦА
# =========================================================
@app.route('/')
def index():
    return render_template('index.html', user=current_user, users=users)

# =========================================================
# БАНКОВСКАЯ СТРАНИЦА
# =========================================================
@app.route('/bank')
def bank():
    balance = users[current_user]['balance']
    return render_template('bank.html', user=current_user, balance=balance)

# =========================================================
# УРОВЕНЬ 1: УЯЗВИМАЯ ПЕРЕВОД (БЕЗ ЗАЩИТЫ) — НЕ ТРОГАЕМ
# =========================================================
@app.route('/transfer_vulnerable', methods=['GET', 'POST'])
def transfer_vulnerable():
    """УЯЗВИМОСТЬ: Нет проверки CSRF-токена!"""
    if request.method == 'POST':
        to_user = request.form.get('to_user')
        amount = int(request.form.get('amount', 0))

        if to_user in users and amount > 0:
            users[current_user]['balance'] -= amount
            users[to_user]['balance'] += amount
            return render_template('transfer.html', 
                                  user=current_user,
                                  balance=users[current_user]['balance'],
                                  message=f"✅ Перевод {amount} пользователю {to_user} выполнен (УЯЗВИМЫЙ метод!)")

    return render_template('transfer.html', 
                          user=current_user,
                          balance=users[current_user]['balance'],
                          message="⚠️ Этот перевод УЯЗВИМ к CSRF-атакам!")

# =========================================================
# УРОВЕНЬ 2: ЗАЩИЩЁННАЯ ПЕРЕВОД (РУЧНАЯ ПРОВЕРКА)
# =========================================================
@app.route('/transfer_protected', methods=['GET', 'POST'])
def transfer_protected():
    """ЗАЩИТА: Ручная проверка CSRF-токена."""
    
    if request.method == 'POST':
        # Получаем токены из запроса и куки
        token_from_request, token_from_cookie = csrf._get_tokens_from_request()
        
        # Проверяем, что токены присутствуют
        if not token_from_request or not token_from_cookie:
            return "CSRF: Missing token", 403
        
        # Проверяем подпись токенов
        validator = CSRFToken(csrf.secret_key, csrf.config)
        if not validator.validate(token_from_request) or not validator.validate(token_from_cookie):
            return "CSRF: Invalid token signature", 403
        
        # Проверяем, что токены совпадают
        if not hmac.compare_digest(token_from_request, token_from_cookie):
            return "CSRF: Token mismatch", 403
        
        # --- ЗАЩИТА ПРОШЛА ---
        to_user = request.form.get('to_user')
        amount = int(request.form.get('amount', 0))

        if to_user in users and amount > 0:
            users[current_user]['balance'] -= amount
            users[to_user]['balance'] += amount
            return render_template('transfer.html', 
                                  user=current_user,
                                  balance=users[current_user]['balance'],
                                  message=f"✅ Перевод {amount} пользователю {to_user} выполнен (ЗАЩИЩЁННО!)")

    # GET-запрос: просто показываем форму с токеном
    return render_template('transfer.html', 
                          user=current_user,
                          balance=users[current_user]['balance'],
                          protected=True,
                          message="🛡️ Этот перевод ЗАЩИЩЁН CSRF-токеном!")

# =========================================================
# УРОВЕНЬ 3: СИМУЛЯТОР АТАКИ (ЗЛОУМЫШЛЕННИК)
# =========================================================
@app.route('/attacker')
def attacker():
    """Страница злоумышленника с поддельной формой"""
    return render_template('attacker.html', victim=current_user)

# =========================================================
# ЗАПУСК
# =========================================================
if __name__ == '__main__':
    print("""
    🔐 CSRF-LAB ЗАПУЩЕНА!
    ======================
    🌐 Открой: http://127.0.0.1:5000
    👤 Текущий пользователь: alice
    ⚠️ ТОЛЬКО ДЛЯ ОБРАЗОВАТЕЛЬНЫХ ЦЕЛЕЙ!
    """)
    app.run(debug=True, host='127.0.0.1', port=5000)