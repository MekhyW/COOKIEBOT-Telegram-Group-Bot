from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from jwcrypto import jwk
import jwt
from jwt.algorithms import RSAAlgorithm
import psutil
import gunicorn.app.base
import hashlib
import hmac
from typing import Dict
from dotenv import load_dotenv
import os
import time
import json
load_dotenv()

app = Flask("Cookiebot")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
cors = CORS(app, resources={r"/login": {"origins": "*"}})
public_key = jwk.JWK.generate(kty='RSA', size=2048, alg='RS256', use='sig', kid='cookiebot-2025')
private_key = jwk.JWK.from_json(public_key.export_private())

def validate_telegram_auth(auth_data: Dict[str, str], bot_token: str) -> bool:
    """
    Validates the hash of Telegram auth data to ensure its authenticity.
    :param auth_data: A dictionary containing Telegram authorization data including 'hash'.
    :param bot_token: The bot token provided by BotFather.
    :return: True if the provided hash matches the computed hash, False otherwise.
    """
    provided_hash = auth_data.pop('hash', None)
    if not provided_hash:
        return False
    data_check_string = "\n".join(f"{key}={auth_data[key]}" for key in sorted(auth_data.keys()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return provided_hash == calculated_hash

def generate_jwt_token(key, sub, iss):
    current_time_in_seconds = round(time.time())
    expiry_time_in_seconds = current_time_in_seconds + 1800 # 30 minutes
    claims = {
        "exp": expiry_time_in_seconds,
        "iat": current_time_in_seconds,
        "kid": key.kid,
        "sub": sub,
        "iss": iss
    }
    private_key = RSAAlgorithm.from_jwk(json.dumps(key))
    signed_jwt = jwt.encode(claims, private_key, algorithm="RS256")
    return signed_jwt

@app.route('/')
def home():
    return jsonify({'status': 'Bot is online'})

@app.route('/login', methods=['POST'])
def generate_key():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400
    valid_tokens = [
        str(os.getenv('cookiebotTOKEN')),
        str(os.getenv('bombotTOKEN')), 
        str(os.getenv('pawstralbotTOKEN')),
        str(os.getenv('tarinbotTOKEN')),
        str(os.getenv('connectbotTOKEN'))
    ]
    for token in valid_tokens:
        if validate_telegram_auth(data, token):
            jwt_token = generate_jwt_token(public_key, data['id'], request.url_root.rstrip('/'))
            return jsonify({
                'status': 'Token generated',
                'accessToken': jwt_token
            })
    return jsonify({'error': 'Invalid bot token'}), 401

@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    jwks_dict = {
        'keys': [json.loads(public_key.export_public())]
    }
    return jsonify(jwks_dict)

@app.route('/.well-known/openid-configuration', methods=['GET'])
def openid_configuration():
    base_url = request.url_root.rstrip('/')
    return jsonify({
        'issuer': base_url,
        'jwks_uri': f'{base_url}/.well-known/jwks.json',
        'response_types_supported': ['id_token'],
        'subject_types_supported': ['public'],
        'id_token_signing_alg_values_supported': ['RS256']
    })

class GunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def run_api_server(debug=False):
    options = {
        'bind': '0.0.0.0:8080',
        'workers': 2,
        'worker_class': 'sync',
        'timeout': 30,
        'reload': debug
    }
    GunicornApplication(app, options).run()

def kill_api_server():
    for proc in psutil.process_iter():
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == 8080:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == '__main__':
    run_api_server(debug=True)
