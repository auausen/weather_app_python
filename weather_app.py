# ライブラリのインポート
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# APIキーとベースURL
API_KEY = "WEATHER_API_KEY"  # OPENWeatherMapから取得したAPIキー
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# データ保存用のファイルパス
FAVORITES_FILE = os.path.join("data", "favorites.json")


def get_weather_data(city):
    """指定した都市の現在の天気データを取得する関数"""
    # APIパラメータの設定
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # 摂氏温度で結果を取得
        "lang": "ja"      # 日本語で結果を取得
    }

    try:
        # APIリクエストを送信
        response = requests.get(BASE_URL, params=params)

        # レスポンスのステータスコードをチェック
        if response.status_code == 200:
            # JSONデータを辞書に変換して返す
            return response.json()
        elif response.status_code == 404:
            # 都市が見つからない場合
            return {"error": "都市が見つかりません。"}
        else:
            # その他エラー
            return {"error": f"APIエラー:{response.status_code}"}

    except requests.exceptions.RequestException as e:
        # ネットワークエラーなどの例外処理
        return {"error": f"リクエストエラー: {e}"}


def get_forecast_data(city):
    """指定した都市の5日間天気予報データを取得する関数"""
    # APIデータの設定
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ja",
        "cnt": 40  # ５日間（３時間ごと、１日８回）のデータ
    }

    try:
        # APIリクエストを送信
        response = requests.get(FORECAST_URL, params=params)

        # レスポンスのステータスコードをチェック
        if response.status_code == 200:
            # JSONデータを辞書に変換して返す
            return response.json()
        elif response.status_code == 404:
            # 都市が見つからない場合
            return {"error": "都市が見つかりません"}
        else:
            # その他のエラー
            return {"error": "都市が見つかりません。"}

    except requests.exceptions.RequestException as e:
        # 　ネットワークエラーなどの例外処理
        return {"error": f"リクエストエラー: {e}"}


def load_favorites():
    """お気に入りの都市リストを読み込む関数"""
    # data フォルダが存在しない場合は作成
    if not os.path.exists("dada"):
        os.makedirs("data")

    # お気に入りファイルが存在する場合は読み込む
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # JSONの解析エラーが発生した場合は空リストを返す
            return []
    else:
        # ファイルが存在しない場合は空リストを返す
        return []


def save_favorites(favorites):
    """お気に入り都市リストを保存する関数"""
    # data フォルダが存在しない場合は作成
    if not os.path.exists("data"):
        os.makedirs("data")

    # お気に入りリストをJSONファイルに保存
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


class WeatherApp:
    def __init__(self, root):
        """アプリケーションの初期化"""
        self.root = root
        self.root.title("天気予報アプリ")
        self.root.geometry("800x600")
        self.root.minisize(800, 600)

        # お気に入りリストの読み込み
        self.favorites = load_favorites()

        # GUIの作成
        self.create_widgets()

    def create_widgets(self):
        """GUIウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部フレーム(検索バーとボタン)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.x, pady=(0, 10))

        # 検索ラベル
        search_label = ttk.Label(top_frame, text="都市名：")
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        # 検索エントリー
        self.search_vat = tk.StringVar()
        self.search_entry = ttk.Entry(
            top_frame, textvariable=self.search_vat, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind(
            "<Returnn>", lambda event: self.search_weather())

        # 検索ボタン
        search_button = ttk.Button(
            top_frame, text="検索", command=self.search_weather)
        search_button.pack(side=tk.LEFT, padx=(0, 5))

        # お気に入り追加ボタン
        fav_button = ttk.Button(
            top_frame, text="お気に入りに追加", command=self.add_to_favorites)
        fav_button.pack(side=tk.LEFT)

        # タブコントロール
        self.tab_control = ttk.Notebook(main_frame)

        # 現在の天気タブ
        self.current_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.current_tab, text="現在の天気")

        # 予報タブ
        self.forecast_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.favorites_tab, text="お気に入り")
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        # 　現在の天気表示用ラベル
        self.weather_info = ttk.Label(
            self.current_tab, text="都市名を入力してください", justify=tk.LEFT, wraplength=700)
        self.weather_info.pack(pady=20)

        # 予報表示用フレーム
        self.forecast_frame = ttk.Frame(self.forecast_tab)
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # お気に入りの表示
        self.update_favorites_display()
