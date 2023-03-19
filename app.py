import requests
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SECRET_KEY"] = "mysecretkey"

db = SQLAlchemy(app)



class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=5da06aa0d8f4d77921ccb56e5bdc5f42"

    r = requests.get(url).json()
    return r


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        error = None

        new_city = request.form.get('city')
        
        if new_city:
            existing_city = City.query.filter_by(name=new_city).first()
            if not existing_city:
                if get_weather_data(new_city)["cod"] == 200:
                    new_city_obj = City(name=new_city)
                    db.session.add(new_city_obj)
                    db.session.commit()
                else:
                    error = 'City does not exist in the world!'
            else:
                error = 'City already exists in database!'
                
        if error:
            flash(error, 'error')
        else:
            flash('City added successfully!', 'success')
            
    cities = City.query.all()

    weather_data = []
    
    for city in cities:
        
        r = get_weather_data(city.name)
        
        # print(r)
        weather = {
            "city": city.name,
            "temperature": r["main"]["temp"],
            "description": r["weather"][0]["description"],
            "icon": r["weather"][0]["icon"]
        }
        weather_data.append(weather)

    
    return render_template('weather.html', weather_data=weather_data)

@app.route('/delete/<name>')
def delete_city(name):
    City.query.filter_by(name=name).delete()
    db.session.commit()
    flash(f'Successfully deleted {name}!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
