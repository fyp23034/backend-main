from flask import Flask, Blueprint
from emails import emails
from metrics import metrics
from pref import pref

app = Flask(__name__)
app.register_blueprint(emails, url_prefix='/emails')
app.register_blueprint(metrics, url_prefix='/metrics')
app.register_blueprint(pref, url_prefix='/pref')

if __name__ == '__main__':
    app.run(debug=True)