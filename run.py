import tkinter as tk
from tkinter import messagebox, colorchooser
import time
import tkinter.ttk as ttk
import sqlite3
import webbrowser
import folium
import os


class Scooter:
    def __init__(self, id, name, latitude, longitude):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.is_available = True


class ScooterRentalApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Прокат самокатов")
        self.master.geometry("700x400")

        self.scooters = [
            Scooter(1, "Самокат 1", 55.7522, 37.6156),
            Scooter(2, "Самокат 2", 55.7517, 37.6171),
            Scooter(3, "Самокат 3", 55.7510, 37.6161),
        ]

        self.create_login_screen()
        self.set_dialog_style()
        self.create_database()

        self.map_path = "map.html"
        self.map_loaded = False
        self.trip_history_window = None

    def set_dialog_style(self):
        style = ttk.Style()
        style.configure("TFrame", background="#e6e6e6")
        style.configure("TLabel", background="#e6e6e6")
        style.configure("TButton", background="#e6e6e6", borderwidth=0)
        style.map(
            "TButton",
            background=[("pressed", "#d9d9d9"), ("active", "#ececec")],
            foreground=[("pressed", "#000000"), ("active", "#000000")]
        )

    def create_database(self):
        self.connection = sqlite3.connect("trip_history.db")
        self.cursor = self.connection.cursor()

        # Create a table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY AUTOINCREMENT, scooter_id INTEGER, "
            "start_time INTEGER, end_time INTEGER, cost REAL)"
        )

    def create_login_screen(self):
        self.clear_screen()

        self.username_label = tk.Label(self.master, text="Имя пользователя:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Пароль:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Войти", command=self.login)
        self.login_button.pack()

    def create_main_screen(self):
        self.clear_screen()
        self.master.geometry("600x400")
        self.scooter_label = tk.Label(self.master, text="Доступные самокаты:")
        self.scooter_label.pack()

        self.scooter_listbox = tk.Listbox(self.master)
        self.scooter_listbox.pack()

        for scooter in self.scooters:
            self.scooter_listbox.insert(tk.END, f"{scooter.name} (ID: {scooter.id})")

        self.select_button = tk.Button(self.master, text="Выбрать самокат", command=self.select_scooter)
        self.select_button.pack()

        self.trip_history_button = tk.Button(self.master, text="История поездок", command=self.show_trip_history)
        self.trip_history_button.pack()

        self.logout_button = tk.Button(self.master, text="Выйти", command=self.logout)
        self.logout_button.pack()

        self.load_map_button = tk.Button(self.master, text="Загрузить карту", command=self.load_map)
        self.load_map_button.pack()

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Perform authentication logic here
        # ...

        self.create_main_screen()

    def logout(self):
        # Perform logout logic here
        # ...
        self.create_login_screen()

    def select_scooter(self):
        selected_index = self.scooter_listbox.curselection()

        if selected_index:
            selected_scooter = self.scooters[selected_index[0]]
            if selected_scooter.is_available:
                selected_scooter.is_available = False
                self.show_trip_timer(selected_scooter)
            else:
                messagebox.showerror("Ошибка", "Самокат уже занят")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите самокат")

    def show_trip_timer(self, scooter):
        self.clear_screen()
        self.trip_start_time = time.time()
        self.current_scooter = scooter

        self.trip_timer_label = tk.Label(self.master, text="Время поездки:")
        self.trip_timer_label.pack()

        self.trip_timer = tk.Label(self.master, text="00:00:00")
        self.trip_timer.pack()

        self.trip_cost_label = tk.Label(self.master, text="Стоимость поездки:")
        self.trip_cost_label.pack()

        self.trip_cost = tk.Label(self.master, text="0")
        self.trip_cost.pack()

        self.end_trip_button = tk.Button(self.master, text="Завершить поездку", command=self.end_trip)
        self.end_trip_button.pack()

        self.update_trip_timer()

    def update_trip_timer(self):
        elapsed_time = int(time.time() - self.trip_start_time)
        hours = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        seconds = elapsed_time % 60
        time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.trip_timer.config(text=time_string)

        self.calculate_trip_cost(elapsed_time)

        self.master.after(1000, self.update_trip_timer)

    def calculate_trip_cost(self, elapsed_time):
        # Calculate the cost based on the elapsed time
        # ...
        cost = elapsed_time * 0.1
        self.trip_cost.config(text=f"{cost:.2f}")

    def end_trip(self):
        end_time = time.time()
        elapsed_time = int(end_time - self.trip_start_time)

        # Save the trip details to the database
        self.cursor.execute(
            "INSERT INTO trips (scooter_id, start_time, end_time, cost) VALUES (?, ?, ?, ?)",
            (self.current_scooter.id, self.trip_start_time, end_time, self.trip_cost.cget("text"))
        )
        self.connection.commit()

        self.current_scooter.is_available = True
        self.create_main_screen()

    def show_trip_history(self):
        self.clear_screen()

        self.trip_history_window = tk.Toplevel(self.master)
        self.trip_history_window.title("История поездок")
        self.trip_history_window.geometry("600x400")

        self.trip_history_label = tk.Label(self.trip_history_window, text="История поездок:")
        self.trip_history_label.pack()

        self.trip_history_listbox = tk.Listbox(self.trip_history_window)
        self.trip_history_listbox.pack()

        # Retrieve trip history from the database
        self.cursor.execute("SELECT * FROM trips")
        trips = self.cursor.fetchall()

        for trip in trips:
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trip[2]))
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trip[3]))
            self.trip_history_listbox.insert(tk.END, f"Самокат ID: {trip[1]}, Начало: {start_time}, Конец: {end_time}, Стоимость: {trip[4]}")

        self.close_trip_history_button = tk.Button(self.trip_history_window, text="Закрыть", command=self.close_trip_history)
        self.close_trip_history_button.pack()

    def close_trip_history(self):
        self.trip_history_window.destroy()

    def load_map(self):
        self.clear_screen()
        self.map_loaded = True

        self.map_label = tk.Label(self.master, text="Карта самокатов")
        self.map_label.pack()

        self.map_frame = tk.Frame(self.master)
        self.map_frame.pack()

        self.map = folium.Map(location=[55.7522, 37.6156], zoom_start=15)
        for scooter in self.scooters:
            folium.Marker([scooter.latitude, scooter.longitude], popup=scooter.name).add_to(self.map)

        self.map.save(self.map_path)

        self.map_view_button = tk.Button(self.map_frame, text="Просмотреть карту", command=self.view_map)
        self.map_view_button.pack()

    def view_map(self):
        # Открываем файл карты в браузере
        map_url = "file://" + os.path.abspath(self.map_path)
        webbrowser.open_new(map_url)

root = tk.Tk()
app = ScooterRentalApp(root)
root.mainloop()
