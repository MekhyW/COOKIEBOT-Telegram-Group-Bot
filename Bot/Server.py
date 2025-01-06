from flask import Flask, jsonify, request
from jwcrypto import jwk
import psutil

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

def run_api_server(debug=False):
    app.run(debug=debug, host="0.0.0.0", port=5000)

def kill_api_server():
    for proc in psutil.process_iter():
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == 5000:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == '__main__':
    run_api_server(debug=True)
