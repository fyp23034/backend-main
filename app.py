from flask import Flask, Blueprint, request, Response
from flask_cors import CORS
from emails import emails
from metrics import metrics
from pref import pref

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'
app.register_blueprint(emails, url_prefix='/emails')
app.register_blueprint(metrics, url_prefix='/metrics')
app.register_blueprint(pref, url_prefix='/pref')

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        res.headers['Access-Control-Allow-Origin'] = '*'
        res.headers['Access-Control-Allow-Methods'] = '*'
        res.headers['Access-Control-Allow-Headers'] = '*'
        return res

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)