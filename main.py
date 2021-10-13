from backend import GetSongs
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
import sys
from pygame import mixer
from temp_songs import songs_list
import requests
import threading
import time
import webbrowser


class Music(QMainWindow):
    def __init__(self):
        super(Music, self).__init__()
        loadUi("design.ui", self)  # loading the design ui
        mixer.init()
        self.songs_list = songs_list
        self.stopped = False
        self.initUi()

    def initUi(self):
        self.name_1.setReadOnly(True)
        self.name_2.setReadOnly(True)
        self.name_3.setReadOnly(True)
        self.name_4.setReadOnly(True)
        self.song_name.setReadOnly(True)
        self.artists_details.setReadOnly(True)

        self.explore.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.main_page)
        )
        self.back_to_home.clicked.connect(self.back_to_home_func)
        self.back_to_home_from_details.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.main_page)
        )

        self.play_1.clicked.connect(lambda: self.play_certain_song(0))
        self.play_2.clicked.connect(lambda: self.play_certain_song(1))
        self.play_3.clicked.connect(lambda: self.play_certain_song(2))
        self.play_4.clicked.connect(lambda: self.play_certain_song(3))

        self.details_1.clicked.connect(lambda: self.set_details(0))
        self.details_2.clicked.connect(lambda: self.set_details(1))
        self.details_3.clicked.connect(lambda: self.set_details(2))
        self.details_4.clicked.connect(lambda: self.set_details(3))

        self.pause_music.clicked.connect(self.pause_music_func)
        self.stop_music.clicked.connect(self.stop_music_func)
        self.go_to_song.clicked.connect(self.open_certain_song)

        self.search_music.clicked.connect(self.search_music_thread)

    def search_music_thread(self):
        music_thread = threading.Thread(target=self.search_music_func)
        music_thread.start()

    def search_music_func(self):
        self.preview_lbl.setText("Searching..")
        search_query = self.search_music_2.text()
        self.songs_list = GetSongs.get_songs(search_query)

        if self.songs_list == []:
            self.preview_lbl.setText("No matches")
        else:
            self.set_thumbnails_and_names(self.thumbnail_1, self.name_1, 0)
            self.set_thumbnails_and_names(self.thumbnail_2, self.name_2, 1)
            self.set_thumbnails_and_names(self.thumbnail_3, self.name_3, 2)
            self.set_thumbnails_and_names(self.thumbnail_4, self.name_4, 3)
            self.preview_lbl.setText("Found results")

    def set_thumbnails_and_names(self, thumbnail, name, idx):
        important_info = self.songs_list[idx]
        response = requests.get(important_info["images"])

        with open("images/album_image.png", "wb") as f:
            f.write(response.content)
        pixmap = QPixmap("images/album_image.png")
        thumbnail.setPixmap(pixmap)

        name.setText(str(important_info["name"]))
        name.setCursorPosition(0)

    def set_details(self, idx):
        self.required_info = self.songs_list[idx]
        response = requests.get(self.required_info["images"])

        with open("images/details_image.png", "wb") as f:
            f.write(response.content)
        pixmap = QPixmap("images/details_image.png")
        self.image.setPixmap(pixmap)

        self.song_name.setPlainText(self.required_info["name"])
        text = "                Artists Details\n\n"
        for artist in self.required_info["artist_details"]:
            text += artist[0] + "--  spotify link: " + artist[1] + "\n\n"

        self.artists_details.setPlainText(text)
        self.explicit_label.setText(
            "Explicit : " + str(self.required_info["explicity"])
        )
        self.popularity.setText("Popularity : " + str(self.required_info["popularity"]))
        self.release_date.setText(
            "Release Date : " + self.required_info["release_date"]
        )

        self.stackedWidget.setCurrentWidget(self.details_page)

    def open_certain_song(self):
        webbrowser.open(self.required_info["song_url"])

    def pause_music_func(self):
        if self.pause_music.text() == "Pause":
            if mixer.music.get_busy():
                self.pause_music.setText("Unpause")
                mixer.music.pause()
        else:
            self.pause_music.setText("Pause")
            mixer.music.unpause()

    def music_stop_check(self, idx):
        start = time.time()
        while True:
            time.sleep(1)
            end = time.time()
            if (
                mixer.music.get_busy() == False
                and end - start >= 30
                and self.pause_music.text() == "Pause"
            ):
                webbrowser.open(self.songs_list[idx]["song_url"])
                self.preview_lbl.setText("Preview done")
                break

            if self.stopped:
                break

    def play_certain_song(self, idx):
        self.stopped = False
        url = self.songs_list[idx]["preview_link"]
        r = requests.get(url, allow_redirects=True)

        self.pause_music.setText("Pause")

        mixer.music.stop()
        try:
            song_name = "Songs_mp3/song.mp3"
            with open(song_name, "wb") as f:
                f.write(r.content)
        except Exception as e:
            song_name = "songs_mp3/song2.mp3"
            with open(song_name, "wb") as f:
                f.write(r.content)
        mixer.music.load(song_name)
        self.preview_lbl.setText("")
        self.music_thread = threading.Thread(target=self.music_stop_check, args=(idx,))
        self.music_thread.start()
        mixer.music.play()

    def back_to_home_func(self):
        self.stackedWidget.setCurrentWidget(self.intro_page)

    def stop_music_func(self):
        mixer.music.stop()
        self.stopped = True
        self.pause_music.setText("Pause")


app = QApplication(sys.argv)
window = Music()
window.show()
app.exec_()
