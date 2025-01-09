from flask import Flask, jsonify, request
from jwcrypto import jwk
import psutil
import gunicorn.app.base

app = Flask("Cookiebot")

key = jwk.JWK.generate(kty='RSA', size=2048, alg='RS256', use='sig', kid='cookiebot-2025')

@app.route('/')
def home():
    return jsonify({'status': 'Bot is online'})

@app.route('/.well-known/jwks.json')
def jwks():
    jwks_dict = {
        'keys': [key.export_public()]
    }
    return jsonify(jwks_dict)

@app.route('/.well-known/openid-configuration')
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
