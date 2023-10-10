from flask import Flask, Blueprint
from emails import emails

app = Flask(__name__)
app.register_blueprint(emails, url_prefix='/emails')

if __name__ == '__main__':
    app.run(debug=True)