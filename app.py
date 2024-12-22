from flask import Flask
from api_req import Weather
from api_key import API_KEY
from dash_app import init_dash

app = Flask(__name__)
weather_api = Weather(API_KEY)

# Инициализация Dash-приложения
dash_app = init_dash(app)

if __name__ == '__main__':
    app.run(debug=True)