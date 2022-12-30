import datetime
import re
import time
from urllib.parse import urljoin
import numpy as np
import requests
from django.shortcuts import render
import plotly.express as px
import urllib.request
import json
from bs4 import BeautifulSoup as bs
from folium import TileLayer, LayerControl
from plotly.offline import plot
import folium
import lxml
from geopy.geocoders import Nominatim

# Create your views here.
def index(request):

    OpenWeatherAPIKey = ''

    if request.method == 'POST':

        city = request.POST.get('city')
        country = request.POST.get('country')
        data = {}

        if city is None or city == '':
            data.update({"error1": str("You need to write something here.")})
        else:
            today = datetime.date.today()
            CurrentWeather = requests.get('https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&appid='+ OpenWeatherAPIKey)
            Hourly_And_5Days_Forecast = requests.get('https://api.openweathermap.org/data/2.5/forecast?q=' + city + '&units=metric&appid='+ OpenWeatherAPIKey)


            ListOfData1 = CurrentWeather.json()
            ListOfData2 = Hourly_And_5Days_Forecast.json()

            if ListOfData1["cod"] == "404" or ListOfData2["cod"] == "404":
                data.update({"error1": str("This doesn't seem to be a city. Please try some other city name.")})
            else:

                ######################________GRAPH________######################
                x = []
                y = []

                now = datetime.datetime.now()
                now = now.strftime("%Y-%m-%d %H:%M:%S")

                if now < ListOfData2['list'][0]['dt_txt']:
                    x.append(now)
                    y.append(ListOfData1['main']['temp'])

                for i in range(9):
                    x.append(ListOfData2['list'][i]['dt_txt'])
                    y.append(ListOfData2['list'][i]['main']['temp'])

                fig = px.line(
                    x=x, y=y,
                    title="Hourly Forecast", height=500
                )

                fig.update_layout(
                    xaxis_title="Date And Hour",
                    yaxis_title="Temperature in °C",
                )

                fig.update_yaxes(ticksuffix=" °C")

                graph = plot(fig, output_type='div')

                ######################________5 DAY FORECAST________######################

                temp_sum1 = 0
                temp_sum2 = 0
                temp_sum3 = 0
                temp_sum4 = 0
                temp_sum5 = 0

                day1 = 0
                day2 = 0
                day3 = 0
                day4 = 0
                day5 = 0

                for i in range(0, 8):
                    temp_sum1 += ListOfData2['list'][i]['main']['temp']

                day1 = temp_sum1 / 8

                for i in range(7, 16):
                    temp_sum2 += ListOfData2['list'][i]['main']['temp']

                day2 = temp_sum2 / 8

                for i in range(16, 24):
                    temp_sum3 += ListOfData2['list'][i]['main']['temp']

                day3 = temp_sum3 / 8

                for i in range(24, 32):
                    temp_sum4 += ListOfData2['list'][i]['main']['temp']

                day4 = temp_sum4 / 8

                for i in range(32, 40):
                    temp_sum5 += ListOfData2['list'][i]['main']['temp']

                day5 = temp_sum5 / 8

                day1 = round(day1)
                day2 = round(day2)
                day3 = round(day3)
                day4 = round(day4)
                day5 = round(day5)

                day1_date = today + datetime.timedelta(days=1)
                day2_date = today + datetime.timedelta(days=2)
                day3_date = today + datetime.timedelta(days=3)
                day4_date = today + datetime.timedelta(days=4)
                day5_date = today + datetime.timedelta(days=5)

                ######################________GEOLOCATION________######################

                GeoLocation = requests.get('http://api.openweathermap.org/geo/1.0/direct?q=' + city + '&appid='+ OpenWeatherAPIKey)
                ListOfData3 = GeoLocation.json()

                lat = ListOfData3[0]['lat']
                lon = ListOfData3[0]['lon']

                f = folium.Figure(width=1050, height=325)
                m = folium.Map(location=[lat, lon], min_zoom=1, max_zoom=12, tiles="openstreetmap", zoom_start=10,
                               control_scale=True)

                temp_layer = TileLayer(name='Temperature',
                                       tiles='https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid='+ OpenWeatherAPIKey,
                                       attr='openstreetmap', min_zoom=1, max_zoom=12, max_native_zoom=12, overlay=True, show=True)
                temp_layer.add_to(m)

                clouds_layer = TileLayer(name='Clouds',
                                         tiles='https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid='+ OpenWeatherAPIKey,
                                         attr='openstreetmap', min_zoom=1, max_zoom=12, max_native_zoom=12,
                                         overlay=True, show=False)
                clouds_layer.add_to(m)

                precipitation_layer = TileLayer(name='Precipitation',
                                                tiles='https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid='+ OpenWeatherAPIKey,
                                                attr='openstreetmap', min_zoom=1, max_zoom=12, max_native_zoom=12,
                                                overlay=True, show=False)
                precipitation_layer.add_to(m)

                pressure_layer = TileLayer(name='Sea level pressure',
                                           tiles='https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid='+ OpenWeatherAPIKey,
                                           attr='openstreetmap', min_zoom=1, max_zoom=12, max_native_zoom=12,
                                           overlay=True, show=False)
                pressure_layer.add_to(m)

                wind_layer = TileLayer(name='Wind Speed',
                                       tiles='https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid='+ OpenWeatherAPIKey,
                                       attr='openstreetmap', min_zoom=1, max_zoom=12, max_native_zoom=12, overlay=True, show=False)
                wind_layer.add_to(m)

                LayerControl().add_to(m)
                m = m.add_to(f)

                m = m._repr_html_()

                data.update({
                    "country_code": str(ListOfData1['sys']['country']),
                    "temp": str(ListOfData1['main']['temp']) + ' °C',
                    "pressure": str(ListOfData1['main']['pressure']),
                    "humidity": str(ListOfData1['main']['humidity']),
                    'main': str(ListOfData1['weather'][0]['main']),
                    'icon': ListOfData1['weather'][0]['icon'],
                    "temp_min": str(ListOfData1['main']['temp_min']) + ' °C',
                    "temp_max": str(ListOfData1['main']['temp_max']) + ' °C',
                    "wind": str(ListOfData1['wind']['speed']) + ' m/s',
                    "city": str(ListOfData1['name']),
                    "date": str(today.strftime("%d-%m-%Y")),
                    "graph": graph,
                    "day1": str(day1) + ' °C',
                    "day2": str(day2) + ' °C',
                    "day3": str(day3) + ' °C',
                    "day4": str(day4) + ' °C',
                    "day5": str(day5) + ' °C',
                    "day1_date": day1_date,
                    "day2_date": day2_date,
                    "day3_date": day3_date,
                    "day4_date": day4_date,
                    "day5_date": day5_date,
                    "day1_icon": ListOfData2['list'][3]['weather'][0]['icon'],
                    "day2_icon": ListOfData2['list'][11]['weather'][0]['icon'],
                    "day3_icon": ListOfData2['list'][19]['weather'][0]['icon'],
                    "day4_icon": ListOfData2['list'][27]['weather'][0]['icon'],
                    "day5_icon": ListOfData2['list'][35]['weather'][0]['icon'],
                    "day1_main": ListOfData2['list'][3]['weather'][0]['main'],
                    "day2_main": ListOfData2['list'][11]['weather'][0]['main'],
                    "day3_main": ListOfData2['list'][19]['weather'][0]['main'],
                    "day4_main": ListOfData2['list'][27]['weather'][0]['main'],
                    "day5_main": ListOfData2['list'][35]['weather'][0]['main'],
                    "map": m,
                })
        if country is None or country == '':
            data.update({"error2": str("You need to write something here.")})
        else:
            country = country.replace(" ", "-")
            today = datetime.date.today()
            next_day1 = today + datetime.timedelta(days=1)
            next_day2 = today + datetime.timedelta(days=2)
            next_day3 = today + datetime.timedelta(days=3)
            next_day4 = today + datetime.timedelta(days=4)
            next_day5 = today + datetime.timedelta(days=5)
            MountainWeather = requests.head('https://www.mountain-forecast.com/countries/' + country + '?top100=yes')
            if MountainWeather.status_code != 200:
                data.update({"error2": str("This doesn't seem to be a country. Please try some other country name.")})
            else:
                MountainWeather = requests.get('https://www.mountain-forecast.com/countries/' + country + '?top100=yes')
                MountainSoup = bs(MountainWeather.content, 'html.parser')
                MountainItems = MountainSoup.find('ul', attrs={'class':'b-list-table'}).find_all('li')
                MountainUrls = {item.find('a').get_text() : get_urls_by_elevation(item.find('a')['href']) for item in MountainItems}
                ListOfData4 = {}
                list = []
                ListOfData4.update({"list": list})
                geolocator = Nominatim(user_agent="Weather_App")
                loc = geolocator.geocode(country)
                country_lat = loc.latitude
                country_lon = loc.longitude
                f2_0 = folium.Figure(width=1500, height=600)
                m2_0 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap", zoom_start=6,
                               control_scale=True)

                f2_1 = folium.Figure(width=1500, height=600)
                m2_1 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap",
                                  zoom_start=6,
                                  control_scale=True)

                f2_2 = folium.Figure(width=1500, height=600)
                m2_2 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap",
                                  zoom_start=6,
                                  control_scale=True)

                f2_3 = folium.Figure(width=1500, height=600)
                m2_3 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap",
                                  zoom_start=6,
                                  control_scale=True)

                f2_4 = folium.Figure(width=1500, height=600)
                m2_4 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap",
                                  zoom_start=6,
                                  control_scale=True)

                f2_5 = folium.Figure(width=1500, height=600)
                m2_5 = folium.Map(location=[country_lat, country_lon], min_zoom=1, max_zoom=12, tiles="openstreetmap",
                                  zoom_start=6,
                                  control_scale=True)

                for mountain_name, urls in MountainUrls.items():
                    for url in urls:
                        list_dict = {}
                        list_dict.update({"mountain_name": mountain_name})
                        MountainWeather = requests.get(url)
                        MountainSoup = bs(MountainWeather.content, 'html.parser')
                        MountainForecast = MountainSoup.find('table', attrs={'class': 'forecast__table forecast__table--js'})
                        MountainLocation = MountainSoup.find('div', attrs={'class': 'b-about__wrapper'})
                        MountainLat = MountainLocation.find('span', attrs={'class': 'latitude'})
                        MountainLong = MountainLocation.find('span', attrs={'class': 'longitude'})
                        list_dict.update({"mountain_lat": MountainLat['title']})
                        list_dict.update({"mountain_long": MountainLong['title']})
                        Days = MountainForecast.find('tr', attrs={'data-row': 'days'}).find_all('td')
                        times = MountainForecast.find('tr', attrs={'data-row': 'time'}).find_all('td')
                        winds = MountainForecast.find('tr', attrs={'data-row': 'wind'}).find_all('div', attrs={'class': 'wind-icon'})
                        winds_direction = MountainForecast.find('tr', attrs={'data-row': 'wind'}).find_all('div', attrs={'class': 'wind-icon__tooltip'})
                        summaries = MountainForecast.find('tr', attrs={'data-row': 'summary'}).find_all('td')
                        rains = MountainForecast.find('tr', attrs={'data-row': 'rain'}).find_all('td')
                        snows = MountainForecast.find('tr', attrs={'data-row': 'snow'}).find_all('td')
                        max_temps = MountainForecast.find('tr', attrs={'data-row': 'max-temperature'}).find_all('td')
                        min_temps = MountainForecast.find('tr', attrs={'data-row': 'min-temperature'}).find_all('td')
                        date_dict = {}
                        a = 0

                        for i, day in enumerate(Days):
                            current_day = SpaceRemover(day.get_text())
                            elevation = url.rsplit('/', 1)[-1]
                            list_dict.update({"elevation": elevation})
                            num_cols = int(day['colspan'])
                            if current_day != '':

                                date = str(datetime.date(datetime.date.today().year, datetime.date.today().month, int(current_day.split(' ')[1])))
                                current_day_dict = {}
                                if i == 0:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"today": current_day_dict})
                                    data.update({
                                        "today": today,
                                    })
                                elif i == 1:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"next_day1": current_day_dict})
                                    data.update({
                                        "next_day1": next_day1,
                                    })
                                elif i == 2:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"next_day2": current_day_dict})
                                    data.update({
                                        "next_day2": next_day2,
                                    })
                                elif i == 3:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"next_day3": current_day_dict})
                                    data.update({
                                        "next_day3": next_day3,
                                    })
                                elif i == 4:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"next_day4": current_day_dict})
                                    data.update({
                                        "next_day4": next_day4,
                                    })
                                elif i == 5:
                                    current_day_dict.update({"date_date": date})
                                    date_dict.update({"next_day5": current_day_dict})
                                    data.update({
                                        "next_day5": next_day5,
                                    })

                                time_cell_dict = {}
                                current_day_dict.update({"time_cell": time_cell_dict})
                                AM_str = ""
                                PM_str = ""
                                NIGHT_str = ""

                                for j in range(a, a + num_cols):
                                    data_dict = {}
                                    time_cell = SpaceRemover(times[j].get_text())
                                    wind = SpaceRemover(winds[j]['data-speed'])
                                    wind_direction = SpaceRemover(winds_direction[j].get_text())
                                    summary = SpaceRemover(summaries[j].get_text())
                                    rain = SpaceRemover(rains[j].get_text())
                                    snow = SpaceRemover(snows[j].get_text())
                                    max_temp = SpaceRemover(max_temps[j].get_text())
                                    min_temp = SpaceRemover(min_temps[j].get_text())
                                    if time_cell == 'AM':
                                        data_dict.update({"wind": wind + "km/h " + wind_direction, "summary": summary, "rain": rain + " mm", "snow": snow + " cm", "max_temp": max_temp, "min_temp": min_temp})
                                        time_cell_dict.update({"AM": data_dict})
                                        AM_str = (
                                                    "<h5> <b>" + time_cell + "</h5></b>"
                                                    "<b>Weather summary: </h4></b>" + summary + "<br>" +
                                                    "<b>Min Temp: </b>" + min_temp + " °C" + "<br>" +
                                                    "<b>Max Temp: </b>" + max_temp + " °C" + "<br>" +
                                                    "<b>Wind speed and Direction: </b>" + wind + "km/h " + wind_direction + "<br>" +
                                                    "<b>Rain: </b>" + rain + " mm" + "<br>" +
                                                    "<b>Snow: </b>" + snow + " cm" + "<br>"
                                                )
                                    if time_cell == 'PM':
                                        data_dict.update({"wind": wind + "km/h " + wind_direction, "summary": summary, "rain": rain + " mm", "snow": snow + " cm", "max_temp": max_temp, "min_temp": min_temp})
                                        time_cell_dict.update({"PM": data_dict})
                                        PM_str = (
                                                    "<h5> <b>" + time_cell + "</h5></b>"
                                                    "<b>Weather summary: </h4></b>" + summary + "<br>" +
                                                    "<b>Min Temp: </b>" + min_temp + " °C" + "<br>" +
                                                    "<b>Max Temp: </b>" + max_temp + " °C" + "<br>" +
                                                    "<b>Wind speed and Direction: </b>" + wind + "km/h " + wind_direction + "<br>" +
                                                    "<b>Rain: </b>" + rain + " mm" + "<br>" +
                                                    "<b>Snow: </b>" + snow + " cm" + "<br>"
                                                )
                                    if time_cell == 'night':
                                        data_dict.update({"wind": wind + "km/h " + wind_direction, "summary": summary, "rain": rain + " mm", "snow": snow + " cm", "max_temp": max_temp, "min_temp": min_temp})
                                        time_cell_dict.update({"NIGHT": data_dict})
                                        NIGHT_str = (
                                                    "<h5> <b>NIGHT</h5></b>"
                                                    "<b>Weather summary: </h4></b>" + summary + "<br>" +
                                                    "<b>Min Temp: </b>" + min_temp + " °C" + "<br>" +
                                                    "<b>Max Temp: </b>" + max_temp + " °C" + "<br>" +
                                                    "<b>Wind speed and Direction: </b>" + wind + "km/h " + wind_direction + "<br>" +
                                                    "<b>Rain: </b>" + rain + " mm" + "<br>" +
                                                    "<b>Snow: </b>" + snow + " cm" + "<br>"
                                                )

                                if i == 0:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_0)
                                elif i == 1:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_1)
                                elif i == 2:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_2)
                                elif i == 3:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_3)
                                elif i == 4:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_4)
                                elif i == 5:
                                    popup = folium.Popup(
                                                        "<h4> <b>" + mountain_name + " " + elevation + " m </h4></b><br>" +
                                                        AM_str + PM_str + NIGHT_str,
                                                        min_width=300, max_width=300)
                                    folium.Marker(location=[MountainLat['title'], MountainLong['title']], popup=popup).add_to(m2_5)
                                a = a + num_cols

                                list_dict.update({"date": date_dict})

                        list.append(list_dict)
                        #print(ListOfData4)
                m2_0 = m2_0.add_to(f2_0)
                m2_0 = m2_0._repr_html_()

                m2_1 = m2_1.add_to(f2_1)
                m2_1 = m2_1._repr_html_()

                m2_2 = m2_2.add_to(f2_2)
                m2_2 = m2_2._repr_html_()

                m2_3 = m2_3.add_to(f2_3)
                m2_3 = m2_3._repr_html_()

                m2_4 = m2_4.add_to(f2_4)
                m2_4 = m2_4._repr_html_()

                m2_5 = m2_5.add_to(f2_5)
                m2_5 = m2_5._repr_html_()
                data.update({
                    "country": country.replace("-", " "),
                    "map2_0": m2_0,
                    "map2_1": m2_1,
                    "map2_2": m2_2,
                    "map2_3": m2_3,
                    "map2_4": m2_4,
                    "map2_5": m2_5,
                })
        #print(data)
    else:
        data = {"start": str("strat")}
    return render(request, "main/index.html", data)


def get_urls_by_elevation(url):
    base_url = 'https://www.mountain-forecast.com/'
    return [urljoin(base_url, url)]


def SpaceRemover(text):
    return re.sub('\s+', ' ', text).strip()