from flask import Flask, render_template, request, redirect, url_for

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = "secretkey"

