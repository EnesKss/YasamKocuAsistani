from PyQt5 import QtWidgets, QtGui, QtCore
from pymongo import MongoClient
import sys
import threading
import time
import random

# MongoDB bağlantısı
client = MongoClient("mongodb://localhost:27017/")
db = client['reminder_app']
users_collection = db['users']
reminders_collection = db['reminders']

# Örnek kullanıcı ekleme (eneskss, şifre: 123, email: kssenes2@gmail.com)
if not users_collection.find_one({"username": "eneskss"}):
    users_collection.insert_one({"username": "eneskss", "password": "123", "email": "kssenes2@gmail.com"})

MOTIVATION_MESSAGES = [
    "Harika bir gün seni bekliyor!",
    "Sen başarabilirsin!",
    "Bugün, hayallerine bir adım daha yaklaşmak için mükemmel bir gün!",
    "Kendine inan ve devam et!",
    "Her şey senin elinde, harika bir iş çıkaracaksın!",
    "Güçlü ol, başarı seni bekliyor!"
]

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kullanıcı Girişi")
        self.setGeometry(300, 300, 400, 300)

        # Arayüz bileşenleri
        self.layout = QtWidgets.QVBoxLayout()

        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setPixmap(QtGui.QPixmap("logo.png").scaled(100, 100, QtCore.Qt.KeepAspectRatio))
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)

        self.username_label = QtWidgets.QLabel("Kullanıcı Adı:")
        self.username_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")

        self.password_label = QtWidgets.QLabel("Şifre:")
        self.password_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Giriş Yap")
        self.login_button.setStyleSheet("background-color: #4682B4; color: white; font-weight: bold; border-radius: 5px;")

        self.forgot_password_button = QtWidgets.QPushButton("Şifremi Unuttum")
        self.forgot_password_button.setStyleSheet("background-color: #87CEEB; color: white; font-weight: bold; border-radius: 5px;")

        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.forgot_password_button)
        self.setLayout(self.layout)

        # Bağlantılar
        self.login_button.clicked.connect(self.handle_login)
        self.forgot_password_button.clicked.connect(self.reset_password)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = users_collection.find_one({"username": username, "password": password})

        if user:
            self.main_window = MainWindow(username)
            self.main_window.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

    def reset_password(self):
        email, ok = QtWidgets.QInputDialog.getText(self, "Şifre Sıfırlama", "Kayıtlı e-posta adresinizi girin:")
        if ok:
            user = users_collection.find_one({"email": email})
            if user:
                QtWidgets.QMessageBox.information(self, "Bilgi", f"Şifreniz sıfırlanabilir. Kullanıcı adı: {user['username']}")
            else:
                QtWidgets.QMessageBox.warning(self, "Hata", "Bu e-posta adresi bulunamadı!")

class MainWindow(QtWidgets.QWidget):
    reminder_signal = QtCore.pyqtSignal(str)  # Sinyal tanımlama

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Hatırlatma Uygulaması")
        self.setGeometry(300, 300, 800, 600)

        # Arayüz bileşenleri
        self.layout = QtWidgets.QVBoxLayout()

        self.greeting_label = QtWidgets.QLabel(f"Hoş geldiniz, {self.username}!")
        self.greeting_label.setFont(QtGui.QFont("Arial", 16))
        self.greeting_label.setAlignment(QtCore.Qt.AlignCenter)
        self.greeting_label.setStyleSheet("color: #4682B4; font-weight: bold;")

        self.task_label = QtWidgets.QLabel("Görev Adı:")
        self.task_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.task_input = QtWidgets.QLineEdit()
        self.task_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")

        self.category_label = QtWidgets.QLabel("Kategori:")
        self.category_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.category_input = QtWidgets.QLineEdit()
        self.category_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")

        self.date_label = QtWidgets.QLabel("Tarih (YYYY-MM-DD):")
        self.date_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.date_input = QtWidgets.QLineEdit()
        self.date_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")

        self.time_label = QtWidgets.QLabel("Saat (HH:MM):")
        self.time_label.setStyleSheet("color: #6A5ACD; font-weight: bold;")
        self.time_input = QtWidgets.QLineEdit()
        self.time_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE;")

        self.add_button = QtWidgets.QPushButton("Hatırlatma Ekle")
        self.add_button.setStyleSheet("background-color: #4682B4; color: white; font-weight: bold; border-radius: 5px;")

        self.reminder_list = QtWidgets.QListWidget()
        self.reminder_list.setStyleSheet("background-color: #E6E6FA; border: 1px solid #B0C4DE;")

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Hatırlatma ara...")
        self.search_input.setStyleSheet("background-color: #F0F8FF; border: 1px solid #B0C4DE; font-weight: bold;")

        self.layout.addWidget(self.greeting_label)
        self.layout.addWidget(self.task_label)
        self.layout.addWidget(self.task_input)
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.category_input)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.time_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.reminder_list)
        self.setLayout(self.layout)

        # Bağlantılar
        self.add_button.clicked.connect(self.add_reminder)
        self.search_input.textChanged.connect(self.search_reminders)

        # Sinyal bağlantısı
        self.reminder_signal.connect(self.show_reminder)

        # Hatırlatma kontrolü için thread başlat
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()

    def add_reminder(self):
        task = self.task_input.text()
        category = self.category_input.text()
        date = self.date_input.text()
        time_ = self.time_input.text()

        if task and category and date and time_:
            reminder = {
                "username": self.username,
                "task": task,
                "category": category,
                "date": date,
                "time": time_,
            }
            reminders_collection.insert_one(reminder)

            self.reminder_list.addItem(f"{task} - {category} - {date} {time_}")
            QtWidgets.QMessageBox.information(self, "Başarılı", "Hatırlatma eklendi!")
            self.task_input.clear()
            self.category_input.clear()
            self.date_input.clear()
            self.time_input.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")

    def search_reminders(self, text):
        self.reminder_list.clear()
        reminders = reminders_collection.find({"username": self.username, "task": {"$regex": text, "$options": "i"}})
        for reminder in reminders:
            self.reminder_list.addItem(f"{reminder['task']} - {reminder['category']} - {reminder['date']} {reminder['time']}")

    def show_reminder(self, message):
        QtWidgets.QMessageBox.information(self, "Hatırlatma", message)

    def check_reminders(self):
        while True:
            current_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm")
            reminders = reminders_collection.find({"username": self.username})
            for reminder in reminders:
                reminder_time = f"{reminder['date']} {reminder['time']}"
                if reminder_time <= current_time:
                    motivation = random.choice(MOTIVATION_MESSAGES)
                    message = f"Görev Zamanı: {reminder['task']}\nKategori: {reminder['category']}\nMotivasyon: {motivation}"
                    self.reminder_signal.emit(message)
                    reminders_collection.delete_one({"_id": reminder['_id']})
            time.sleep(10)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Örnek kullanıcı kaydı (varsa tekrar eklenmez)
    if not users_collection.find_one({"username": "admin"}):
        users_collection.insert_one({"username": "admin", "password": "admin123"})

    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
