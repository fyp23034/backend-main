from flask import Flask, Blueprint
from emails import emails, client

@emails.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'

@emails.route('/next')
def nextEmail():
    return 'next!'