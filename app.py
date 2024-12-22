from flask import Flask, request, render_template

from api_req import Weather
from api_key import API_KEY


api_key = API_KEY

weather_api = Weather(api_key)
app = Flask(__name__)

@app.route('/')
def hello_page():
    return 'Hakuna matata'

@app.route('/trip_weather', methods=['GET', 'POST'])
def check_weather():
    error_codes = {
        400: 'Неправильно введены названия городов',
        401: 'Авторизация не удалась, попробуйте позже',
        403: "Нет доступа к запрашиваемым данным",
        404: "Непрвильно введены названия городов ес",
        500: "Не получилось выполнить запрос, повторите попытку позже"
    }
    if request.method=='GET':
        return render_template('trip_weather_form.html')
    else:
        try:
            #считываем названия городов/убираем цыфры если есть
            city1_name = ''.join(_ for _ in request.form['startPoint'] if not _.isdigit())
            city2_name = ''.join(_ for _ in request.form['endPoint'] if not _.isdigit())

            #получаем данные о погоде в городах
            s_point_data = weather_api.get_weather_data(city1_name)
            e_point_data = weather_api.get_weather_data(city2_name)

            #достаём метрики
            city1_temp = s_point_data["temp"]
            city1_humidity = s_point_data["humidity"]
            city1_wind = s_point_data["wind_speed"]
            city1_rain = s_point_data["rain_prob"]
            city1_weather_type = s_point_data["weather_type"]

            city2_temp = e_point_data["temp"]
            city2_humidity = e_point_data["humidity"]
            city2_wind = e_point_data["wind_speed"]
            city2_rain = e_point_data["rain_prob"]
            city2_weather_type = e_point_data["weather_type"]

            return render_template('trip_weather_reply.html',
                                   city1_name=city1_name.capitalize(),
                                   city1_temp=city1_temp,
                                   city1_humidity=city1_humidity,
                                   city1_wind=city1_wind,
                                   city1_rain=city1_rain,
                                   city1_weather_type=city1_weather_type,
                                   city2_name=city2_name.capitalize(),
                                   city2_temp=city2_temp,
                                   city2_humidity=city2_humidity,
                                   city2_wind=city2_wind,
                                   city2_rain=city2_rain,
                                   city2_weather_type=city2_weather_type
                                   )
        except Exception as e:
            if type(s_point_data)==int:
                return render_template('problem.html', error = error_codes.get(s_point_data, e))
            else:
                return render_template('problem.html', error = error_codes.get(e_point_data, e))
if __name__ == '__main__':
    app.run(debug=True)