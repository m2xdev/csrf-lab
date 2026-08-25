# csrf_shield.py
# Модуль защиты от CSRF для лабораторной работы

import hmac
import hashlib
import secrets
from flask import request, make_response

class CSRFConfig:
    def __init__(self):
        self.cookie_name = 'csrf_token'
        self.header_name = 'X-CSRF-Token'
        self.form_field_name = 'csrf_token'
        self.token_length = 32

class CSRFToken:
    def __init__(self, secret_key, config=None):
        self.secret_key = secret_key.encode('utf-8') if isinstance(secret_key, str) else secret_key
        self.config = config or CSRFConfig()

    def generate(self):
        """Генерирует криптостойкий токен с HMAC-подписью"""
        random_val = secrets.token_hex(self.config.token_length)
        signature = hmac.new(self.secret_key, random_val.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{random_val}.{signature}"

    def validate(self, token_str):
        """Проверяет подпись токена"""
        if not token_str or '.' not in token_str:
            return False
        parts = token_str.split('.', 1)
        if len(parts) != 2:
            return False
        random_val, signature = parts
        expected_sig = hmac.new(self.secret_key, random_val.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_sig)

class CSRFShield:
    def __init__(self, app=None, config=None):
        self.config = config or CSRFConfig()
        self.secret_key = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.secret_key = app.secret_key

    @property
    def get_token(self):
        """Возвращает текущий токен из куки или создает новый"""
        token = request.cookies.get(self.config.cookie_name)
        if not token or not CSRFToken(self.secret_key, self.config).validate(token):
            token = CSRFToken(self.secret_key, self.config).generate()
        return token

    def _get_tokens_from_request(self):
        """Извлекает токены из POST-запроса (форма или заголовки) и из куки"""
        token_from_req = (
            request.form.get(self.config.form_field_name) or
            request.headers.get(self.config.header_name)
        )
        token_from_cookie = request.cookies.get(self.config.cookie_name)
        return token_from_req, token_from_cookie

    def _after_request(self, response):
        """Устанавливает куку с CSRF-токеном в ответ клиенту, если её еще нет"""
        current_cookie = request.cookies.get(self.config.cookie_name)
        if not current_cookie or not CSRFToken(self.secret_key, self.config).validate(current_cookie):
            new_token = CSRFToken(self.secret_key, self.config).generate()
            response.set_cookie(
                self.config.cookie_name,
                new_token,
                httponly=False,  # Должно быть доступно для JS/форм в рамках лабы
                samesite='Lax'
            )
        return response