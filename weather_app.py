# 必要なライブラリのインポート
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# 環境変数の読み込み

# APIキーとベースURL
API_KEY = "WEATHER_APP_KEY"  # .envファイルから取得
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# データ保存用のファイルパス
FAVORITES_FILE = os.path.join("data", "favorites.json")


def get_weather_data(city):
    """指定した都市の現在の天気データを取得する関数"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ja"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": "都市が見つかりません" if response.status_code == 404 else f"APIエラー: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"リクエストエラー: {e}"}


def get_forecast_data(city):
    """指定した都市の5日間天気予報データを取得する関数"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ja",
        "cnt": 40
    }

    try:
        response = requests.get(FORECAST_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": "都市が見つかりません" if response.status_code == 404 else f"APIエラー: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"リクエストエラー: {e}"}


def load_favorites():
    """お気に入りの都市リストを読み込む関数"""
    os.makedirs("data", exist_ok=True)
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_favorites(favorites):
    """お気に入り都市リストを保存する関数"""
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("天気予報アプリ")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.favorites = load_favorites()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 検索バー
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_frame, text="都市名:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self.search_weather())

        ttk.Button(top_frame, text="検索", command=self.search_weather).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="お気に入りに追加",
                   command=self.add_to_favorites).pack(side=tk.LEFT)

        # タブコントロール
        self.tab_control = ttk.Notebook(main_frame)

        self.current_tab = ttk.Frame(self.tab_control)
        self.forecast_tab = ttk.Frame(self.tab_control)
        self.favorites_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.current_tab, text="現在の天気")
        self.tab_control.add(self.forecast_tab, text="5日間予報")
        self.tab_control.add(self.favorites_tab, text="お気に入り")
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        # 現在の天気表示
        self.weather_info = ttk.Label(
            self.current_tab, text="都市名を入力してください", wraplength=700)
        self.weather_info.pack(pady=20)

        # 予報表示エリア
        self.forecast_frame = ttk.Frame(self.forecast_tab)
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # お気に入り表示
        self.favorites_frame = ttk.Frame(self.favorites_tab)
        self.favorites_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.update_favorites_display()

    def search_weather(self):
        city = self.search_var.get().strip()
        if not city:
            messagebox.showinfo("情報", "都市名を入力してください")
            return

        if (weather_data := get_weather_data(city)).get("error"):
            messagebox.showerror("エラー", weather_data["error"])
            return

        self.display_current_weather(weather_data)

        if (forecast_data := get_forecast_data(city)).get("error") is None:
            self.display_forecast(forecast_data)

    def display_current_weather(self, data):
        try:
            info = f"""
都市: {data['name']} ({data['sys']['country']})
天気: {data['weather'][0]['description']}
気温: {data['main']['temp']}°C (体感 {data['main']['feels_like']}°C)
最低/最高: {data['main']['temp_min']}°C / {data['main']['temp_max']}°C
湿度: {data['main']['humidity']}%
気圧: {data['main']['pressure']} hPa
風速: {data['wind']['speed']} m/s ({self.get_wind_direction(data['wind']['deg'])})
日の出: {datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')}
日の入り: {datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')}
"""
            self.weather_info.config(text=info)
            self.tab_control.select(0)
        except KeyError as e:
            messagebox.showerror("エラー", f"データ解析エラー: {e}")

    def get_wind_direction(self, degrees):
        directions = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東",
                      "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"]
        return directions[round(degrees / 22.5) % 16]

    def display_forecast(self, data):
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.forecast_frame,
                  text=f"{data['city']['name']} ({data['city']['country']}) の5日間予報",
                  font=("", 12, "bold")).pack(pady=10)

        forecast_by_day = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            forecast_by_day.setdefault(date, []).append(item)

        for date, items in forecast_by_day.items():
            frame = ttk.LabelFrame(self.forecast_frame, text=date)
            frame.pack(fill=tk.X, pady=5)

            avg_temp = sum(item['main']['temp'] for item in items) / len(items)
            weathers = [item['weather'][0]['description'] for item in items]
            common_weather = max(set(weathers), key=weathers.count)

            ttk.Label(
                frame, text=f"平均気温: {avg_temp:.1f}°C, 主な天気: {common_weather}").pack()

            hour_frame = ttk.Frame(frame)
            hour_frame.pack()
            for item in items[:5]:
                time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                ttk.Label(hour_frame, text=f"{time}\n{item['main']['temp']}°C\n{item['weather'][0]['description']}").pack(
                    side=tk.LEFT, padx=10)

    def add_to_favorites(self):
        city = self.search_var.get().strip()
        if not city:
            messagebox.showinfo("情報", "都市名を入力してください")
            return

        if city in self.favorites:
            messagebox.showinfo("情報", f"{city}は既に登録されています")
            return

        if get_weather_data(city).get("error"):
            return

        self.favorites.append(city)
        save_favorites(self.favorites)
        self.update_favorites_display()
        messagebox.showinfo("成功", f"{city}をお気に入りに追加しました")

    def update_favorites_display(self):
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()

        if not self.favorites:
            ttk.Label(self.favorites_frame,
                      text="お気に入りがありません\n都市を検索して追加してください").pack(pady=20)
            return

        ttk.Label(self.favorites_frame, text="お気に入り都市",
                  font=("", 12, "bold")).pack()
        for city in self.favorites:
            frame = ttk.Frame(self.favorites_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Button(frame, text=city, width=20,
                       command=lambda c=city: self.search_city(c)).pack(side=tk.LEFT)
            ttk.Button(frame, text="削除",
                       command=lambda c=city: self.remove_favorite(c)).pack(side=tk.LEFT)

    def search_city(self, city):
        self.search_var.set(city)
        self.search_weather()

    def remove_favorite(self, city):
        self.favorites.remove(city)
        save_favorites(self.favorites)
        self.update_favorites_display()
        messagebox.showinfo("成功", f"{city}を削除しました")


if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
