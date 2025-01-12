import time
from calendar import calendar, Calendar
from tkinter import ttk

from tkcalendar import Calendar, DateEntry
import requests
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import urllib.request
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading


def get_weather(city):
    API_KEY = ""
    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric")
    data = response.json()

    if data["cod"] == 200:
        main = data['main']
        country = data["sys"]["country"]
        city = data["name"]
        temperature = main['temp']
        feels_like = main['feels_like']
        weather_description = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        flag_url = f"https://flagcdn.com/48x36/{country.lower()}.png"

        return (flag_url,
                f"Country: {country}\n"
                f"City: {city}\n"
                f"Temperature: {temperature} °C\n"
                f"Feels like: {feels_like} °C\n"
                f"Weather description: {weather_description}",
                icon_url)
    else:
        return None, "City not found", None


def temperature_trend_graph(city):
    API_KEY = ""
    response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric")
    data = response.json()

    temps = []
    times = []

    if data["cod"] == "200":
        temps = [forecast['main']["temp"] for forecast in data["list"]]
        times = [forecast["dt_txt"] for forecast in data["list"]]

    if temps and times:
        fig = Figure(figsize=(4, 4))
        a = fig.add_subplot(111)
        a.plot(times, temps)
        a.set_title(f"Temperature Trend for {city}\n")
        a.set_xlabel("Time")
        a.set_ylabel("Temperature (°C)")
        a.tick_params(axis='x', labelrotation=90)

        canvas = FigureCanvasTkAgg(fig, master=app)
        canvas.draw()
        canvas.get_tk_widget().place(x=500, y=90)

def reset_display():
    displayWeather.configure(text="")

    for widget in app.winfo_children():
        if isinstance(widget, tk.Label):
            widget.place_forget()
            widget.destroy()

    for widget in app.winfo_children():
        if isinstance(widget, FigureCanvasTkAgg):
            widget.get_tk_widget().destroy()

    app.update()

def display_weather_thread():
    reset_display()

    city = cityEntry.get()

    loading_animation()
    loadingLabel.configure(text="")
    flag_url, weather_info, icon_url = get_weather(city)

    displayWeather.configure(text=weather_info)

    for i in range(20):
        displayWeather.place_configure(y=315 - (i * 2))
        displayWeather.update()
        time.sleep(0.02)


    if icon_url:
        urllib.request.urlretrieve(icon_url, "weather_icon.png")
        weather_icon = ImageTk.PhotoImage(Image.open("weather_icon.png"))

        icon_label = tk.Label(app, image=weather_icon)
        icon_label.place(x=200, y=375)
        icon_label.image = weather_icon


    if flag_url:
        urllib.request.urlretrieve(flag_url, "country_flag.png")
        country_flag = ImageTk.PhotoImage(Image.open("country_flag.png"))

        flag_label = tk.Label(app, image=country_flag)
        flag_label.place(x=220, y=230)
        flag_label.image = country_flag

    temperature_trend_graph(city)

def display_weather():
    threading.Thread(target=display_weather_thread).start()

light_image = Image.open("moon-stars (1).png").resize((32, 32))
dark_image = Image.open("brightness.png").resize((32, 32))

lightMode = ctk.CTkImage(light_image=light_image)
darkMode = ctk.CTkImage(light_image=dark_image)

is_dark_mode = True

def theme_toggle():
    global is_dark_mode
    if is_dark_mode:
        ctk.set_appearance_mode("light")
        themeButton.configure(image=darkMode)
    else:
        ctk.set_appearance_mode("dark")
        themeButton.configure(image=lightMode)

    is_dark_mode = not is_dark_mode

def loading_animation():
    loadingTexts = ["Fetching data..", "Fetching data....", "Fetching data......"]
    for text in loadingTexts:
        loadingLabel.configure(text=text)
        app.update()
        time.sleep(0.8)


favorite_cities = []

favoriteImage = Image.open("circle-heart.png")
favImage = ctk.CTkImage(favoriteImage)

viewFavorites = Image.open("eye.png")
viewFav = ctk.CTkImage(viewFavorites)

DeleteIcon = Image.open("trash.png")
Delete = ctk.CTkImage(DeleteIcon)

def add_to_favorites():
    city = cityEntry.get()
    if city and city not in favorite_cities:
        favorite_cities.append(city)

def view_favorites():
    app2 = ctk.CTkToplevel(app)
    app2.title("favorite cities")
    app2.geometry("300x500")

    app2.attributes("-topmost", True)

    favoritesLabel = ctk.CTkLabel(app2, text="Favorite Cities:", font=("Arial", 28, "bold"))
    favoritesLabel.place(x=30, y=20)

    city_checkboxes = {}

    favoritesFrame = tk.Frame(app2)
    favoritesFrame.place(x=35, y=70)

    for city in favorite_cities:
        var = tk.IntVar()
        checkbox = tk.Checkbutton(favoritesFrame, text=city, variable=var, font=("Arial", 14))
        checkbox.pack(anchor="w")

        city_checkboxes[city] = var

    def delete_selected():
        selected_cities = [city for city, var in city_checkboxes.items() if var.get() == 1]

        for city in selected_cities:
            favorite_cities.remove(city)

        app2.destroy()
        view_favorites()

    DeleteButton = ctk.CTkButton(app2, image=Delete, command=delete_selected, text="", width=50)
    DeleteButton.place(x=240, y =20)

def get_weather_prediction(city, futureDateTime):
    API_KEY = "dcfdcc3f4c3a220f9a5af83a257487f9"
    response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric")
    data = response.json()

    if data["cod"] == "200":
        country = data["city"]["country"]
        city_name = data["city"]["name"]

        for forecast in data["list"]:
            if futureDateTime in forecast["dt_txt"]:
                icon_code = forecast['weather'][0]['icon']
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                flag_url = f"https://flagcdn.com/48x36/{country.lower()}.png"
                return (flag_url,
                        country,
                        city_name,
                        forecast['main']['temp'],
                        forecast['main']['feels_like'],
                        forecast['weather'][0]['description'],
                        icon_url)

    return None, "Weather prediction not available.", None

def open_predict():
    app3 = ctk.CTkToplevel(app)
    app3.title("Get weather prediction")
    app3.geometry("500x550")

    app3.attributes("-topmost", True)

    cityLabel = ctk.CTkLabel(app3, text="Enter your city:", font=("Arial", 18, "bold"))
    cityLabel.place(x=40, y=40)

    cityEntry = ctk.CTkEntry(app3, width=200, justify=("center"))
    cityEntry.place(x=190, y=40)

    dateLabel = ctk.CTkLabel(app3, text="Select a Date:", font=("Arial", 18, "bold"))
    dateLabel.place(x=40, y=90)

    calendar = DateEntry(app3, width=17, background='darkblue', foreground='white',font=("Arial", 18), borderwidth=5, state="readonly")
    calendar.place(y=120, x=240)

    timeOptions = ["00:00:00", "03:00:00", "06:00:00", "09:00:00", "12:00:00", "15:00:00", "18:00:00", "21:00:00"]
    timeCombo = ttk.Combobox(app3, values=timeOptions, font=("Arial", 18), state="readonly", width=6, justify="center")
    timeCombo.current(0)
    timeCombo.place(x=500, y=120)

    loadingLabel = ctk.CTkLabel(app3, text="", font=("Arial", 20, "bold"))
    loadingLabel.place(x=185, y=220)

    resultLabel = ctk.CTkLabel(app3, text="", font=("Arial", 14, "bold"))
    resultLabel.place(x=100, y=250)

    def loading_animation():
        loadingTexts = ["Fetching data..", "Fetching data....", "Fetching data......"]
        for text in loadingTexts:
            loadingLabel.configure(text=text)
            app3.update()
            time.sleep(0.8)

    def reset_display():
        resultLabel.configure(text="")

        for widget in app3.winfo_children():
            if isinstance(widget, tk.Label):
                widget.place_forget()
                widget.destroy()

        for widget in app3.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        app3.update()

    def show_prediction():
        reset_display()
        city = cityEntry.get().strip()

        loading_animation()
        loadingLabel.configure(text="")


        futureDate = calendar.get_date().strftime("%Y-%m-%d")
        selectedTime = timeCombo.get()

        futureDateTime = f"{futureDate} {selectedTime}"

        flag_url, country, city_name, temperature, feels_like, weather_description, icon_url = get_weather_prediction(
            city, futureDateTime)


        if icon_url:
            urllib.request.urlretrieve(icon_url, "weather_icon.png")
            weather_icon = ImageTk.PhotoImage(Image.open("weather_icon.png"))

            icon_label = tk.Label(app3, image=weather_icon)
            icon_label.place(x=265, y=450)
            icon_label.image = weather_icon

        if flag_url:
            urllib.request.urlretrieve(flag_url, "country_flag.png")
            country_flag = ImageTk.PhotoImage(Image.open("country_flag.png"))

            flag_label = tk.Label(app3, image=country_flag)
            flag_label.place(x=285, y=260)
            flag_label.image = country_flag

        if temperature is None:
            resultLabel.configure(text="Weather prediction not available.")
        else:
            resultLabel.configure(text=f"Country: {country}\n"
                                       f"City: {city_name}\n"
                                       f"Weather prediction for {futureDateTime}\n"
                                       f"Predicted Temperature: {temperature} °C\n"
                                       f"Feels Like: {feels_like} °C\n"
                                       f"Description: {weather_description}\n")

    getPredictionBtn = ctk.CTkButton(app3, text="Get weather prediction", font=("Arial",15,"bold"), command=show_prediction)
    getPredictionBtn.place(x=190, y=150)

app = ctk.CTk()
app.title("Weather App")
app.geometry("800x550")




themeButton = ctk.CTkButton(app,text="", width=50, image=lightMode, command=theme_toggle)
themeButton.place(x=10, y=10)

label1 = ctk.CTkLabel(app, text="Enter your City:", font=("Arial", 18, "bold"))
label1.place(x=130, y=50)

cityEntry = ctk.CTkEntry(app, width=150, justify="center")
cityEntry.place(x=120, y=90)

weatherButton = ctk.CTkButton(app, text="Get Weather", command=display_weather)
weatherButton.place(x=124, y=140)

loadingLabel = ctk.CTkLabel(app, text="", font=("Arial", 20, "bold"))
loadingLabel.place(x=125, y=220)

displayWeather = ctk.CTkLabel(app, text="", font=("Arial", 12, "bold"))
displayWeather.place(x=105, y=220)

favoriteButton = ctk.CTkButton(app, image=favImage, text="add to favorites", command=add_to_favorites)
favoriteButton.place(x=128, y=400)

viewFavoritesBtn = ctk.CTkButton(app, image=viewFav, text="view favorites", command=view_favorites)
viewFavoritesBtn.place(y=440, x=128 )

predictButton = ctk.CTkButton(app, text="Get weather prediction", font=("Arial",12,"bold"), command=open_predict)
predictButton.place(x=125, y=480)

app.mainloop()
