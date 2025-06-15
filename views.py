import os
from sqlalchemy.orm import sessionmaker
from PyQt5.QtCore import QObject, Qt, QUrl, pyqtSlot
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QDialog, QLabel, QLineEdit, QTextEdit, QFileDialog, QCheckBox, QDesktopWidget
)

from models import FrogsToad, State, Image, AudioFile, TerritoryMap
from utils import copy_file_to_dir

class FrogsMainWindow(QMainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags(), engine=None):
        super().__init__(parent, flags)
        self.engine = engine
        if self.engine:
            self.Session = sessionmaker(bind=self.engine)
        else:
            self.Session = None

        self.setWindowTitle("Frog & Toad Database - Musk Edition")
        self.resize(1000, 700)

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, Qt.white)
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.species_list = QListWidget()
        self.species_list.setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #555;")
        layout.addWidget(self.species_list)

        button_layout = QHBoxLayout()
        self.view_button = QPushButton("View Profile")
        self.edit_button = QPushButton("Edit Profile")
        self.add_button = QPushButton("Add New Species")
        self.map_button = QPushButton("Interactive Map")
        for btn in [self.view_button, self.edit_button, self.add_button, self.map_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3C3C3C;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)

        self.view_button.clicked.connect(self.view_profile)
        self.edit_button.clicked.connect(self.edit_profile)
        self.add_button.clicked.connect(self.add_new)
        self.map_button.clicked.connect(self.show_map)

        self.load_species()

    def load_species(self):
        if self.Session:
            session = self.Session()
            frogs_toads = session.query(FrogsToad).all()
            self.species_list.clear()
            for ft in frogs_toads:
                self.species_list.addItem(ft.name)
            session.close()

    def view_profile(self):
        selected_item = self.species_list.currentItem()
        if selected_item and self.Session:
            session = self.Session()
            frog_toad = session.query(FrogsToad).filter_by(name=selected_item.text()).first()
            if frog_toad:
                profile_view = ProfileView(frog_toad, self.engine)
                profile_view.exec_()
            session.close()

    def edit_profile(self):
        selected_item = self.species_list.currentItem()
        if selected_item and self.Session:
            session = self.Session()
            frog_toad = session.query(FrogsToad).filter_by(name=selected_item.text()).first()
            edit_view = EditView(frog_toad, self.engine)
            edit_view.exec_()
            session.close()
            self.load_species()

    def add_new(self):
        edit_view = EditView(None, self.engine)
        edit_view.exec_()
        self.load_species()

    def show_map(self):
        map_view = MapView(self.engine)
        map_view.show()

class ProfileView(QDialog):
    def __init__(self, frog_toad, engine):
        super().__init__()
        self.frog_toad = frog_toad
        self.engine = engine

        self.setWindowTitle(f"{frog_toad.name} - Profile")
        self.resize(600, 500)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<h2>{frog_toad.name}</h2>"))
        layout.addWidget(QLabel(f"Breeding Season: {frog_toad.breeding_season}"))
        layout.addWidget(QLabel(f"Habitat: {frog_toad.habitat}"))
        layout.addWidget(QLabel(f"Diet: {frog_toad.diet}"))
        layout.addWidget(QLabel(f"Adult Size: {frog_toad.adult_size}"))
        layout.addWidget(QLabel(f"Color Scheme: {frog_toad.color_scheme}"))
        layout.addWidget(QLabel(f"Notes: {frog_toad.profile_notes}"))

        if frog_toad.images:
            image_label = QLabel()
            pixmap = QPixmap(frog_toad.images[0].image_path)
            image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
            layout.addWidget(image_label)

        self.audio_player = QMediaPlayer()
        if frog_toad.audio_files:
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(frog_toad.audio_files[0].audio_path)))
            play_button = QPushButton("Play Call")
            play_button.setStyleSheet("background-color: #3C3C3C; color: white; padding: 5px;")
            play_button.clicked.connect(self.play_audio)
            layout.addWidget(play_button)

        if frog_toad.territory_map:
            map_label = QLabel()
            pixmap = QPixmap(frog_toad.territory_map.map_path)
            map_label.setPixmap(pixmap.scaled(300, 200, Qt.KeepAspectRatio))
            layout.addWidget(map_label)

        states = ", ".join([state.state_name for state in frog_toad.states])
        layout.addWidget(QLabel(f"Native to: {states}"))

        ai_button = QPushButton("Ask Frog & Toad AI")
        ai_button.setStyleSheet("background-color: #FF4500; color: white; padding: 5px;")
        ai_button.clicked.connect(self.ask_ai)
        layout.addWidget(ai_button)

    def play_audio(self):
        self.audio_player.play()

    def ask_ai(self):
        print("AI feature coming soon - Imagine asking about frog calls or habitats!")

class EditView(QDialog):
    def __init__(self, frog_toad=None, engine=None):
        super().__init__()
        print("Starting EditView")
        self.setWindowTitle("Add New Species")
        layout = QVBoxLayout(self)
        label = QLabel("Test Dialog")
        layout.addWidget(label)
        print("Finished EditView")

        # Set window properties
        self.setWindowTitle("Edit Profile" if frog_toad else "Add New Species")
        self.resize(700, 600)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        # Main layout for the dialog
        layout = QVBoxLayout(self)

        # Create scroll area and content widget
        scroll_area = QScrollArea()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Add form fields to content_layout
        self.name_edit = QLineEdit(frog_toad.name if frog_toad else "")
        content_layout.addWidget(QLabel("Name:"))
        content_layout.addWidget(self.name_edit)

        self.breeding_edit = QLineEdit(frog_toad.breeding_season if frog_toad else "")
        content_layout.addWidget(QLabel("Breeding Season:"))
        content_layout.addWidget(self.breeding_edit)

        self.habitat_edit = QLineEdit(frog_toad.habitat if frog_toad else "")
        content_layout.addWidget(QLabel("Habitat:"))
        content_layout.addWidget(self.habitat_edit)

        self.diet_edit = QLineEdit(frog_toad.diet if frog_toad else "")
        content_layout.addWidget(QLabel("Diet:"))
        content_layout.addWidget(self.diet_edit)

        self.size_edit = QLineEdit(frog_toad.adult_size if frog_toad else "")
        content_layout.addWidget(QLabel("Adult Size:"))
        content_layout.addWidget(self.size_edit)

        self.color_edit = QLineEdit(frog_toad.color_scheme if frog_toad else "")
        content_layout.addWidget(QLabel("Color Scheme:"))
        content_layout.addWidget(self.color_edit)

        self.notes_edit = QTextEdit(frog_toad.profile_notes if frog_toad else "")
        content_layout.addWidget(QLabel("Profile Notes:"))
        content_layout.addWidget(self.notes_edit)

        # Image management
        self.image_list = QListWidget()
        if frog_toad and frog_toad.images:
            for image in frog_toad.images:
                self.image_list.addItem(image.image_path)
        self.image_list.setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #555;")
        content_layout.addWidget(QLabel("Images:"))
        content_layout.addWidget(self.image_list)
        add_image_btn = QPushButton("Add Image")
        add_image_btn.clicked.connect(self.add_image)
        content_layout.addWidget(add_image_btn)

        # Audio management
        self.audio_list = QListWidget()
        if frog_toad and frog_toad.audio_files:
            for audio in frog_toad.audio_files:
                self.audio_list.addItem(audio.audio_path)
        self.audio_list.setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #555;")
        content_layout.addWidget(QLabel("Audio Files:"))
        content_layout.addWidget(self.audio_list)
        add_audio_btn = QPushButton("Add Audio")
        add_audio_btn.clicked.connect(self.add_audio)
        content_layout.addWidget(add_audio_btn)

        # Territory map management
        self.map_edit = QLineEdit(frog_toad.territory_map.map_path if frog_toad and frog_toad.territory_map else "")
        self.map_edit.setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #555;")
        content_layout.addWidget(QLabel("Territory Map:"))
        content_layout.addWidget(self.map_edit)
        upload_map_btn = QPushButton("Upload Map")
        upload_map_btn.clicked.connect(self.upload_map)
        content_layout.addWidget(upload_map_btn)

        # State selection with checkboxes
        self.state_checkboxes = []
        states = self.session.query(State).all()
        content_layout.addWidget(QLabel("Native States:"))
        for state in states:
            cb = QCheckBox(state.state_name)
            cb.setStyleSheet("color: white;")
            if frog_toad and state in frog_toad.states:
                cb.setChecked(True)
            self.state_checkboxes.append(cb)
            content_layout.addWidget(cb)

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)

        # Add scroll area to the dialog's layout
        layout.addWidget(scroll_area)

        # Add save button outside the scroll area
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background-color: #FF4500; color: white; padding: 8px;")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        # Rest of your code (e.g., additional methods) goes here

    def add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            dest_path = copy_file_to_dir(file_path, "data/images")
            self.image_list.addItem(dest_path)

    def add_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio (*.mp3 *.wav)")
        if file_path:
            dest_path = copy_file_to_dir(file_path, "data/audio")
            self.audio_list.addItem(dest_path)

    def upload_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Map Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            dest_path = copy_file_to_dir(file_path, "data/maps")
            self.map_edit.setText(dest_path)

    def save(self):
        if not self.Session:
            print("No database session available.")
            return

        session = self.Session()
        images = [self.image_list.item(i).text() for i in range(self.image_list.count())]
        audio_files = [self.audio_list.item(i).text() for i in range(self.audio_list.count())]
        states = [cb.text() for cb in self.state_checkboxes if cb.isChecked()]

        if self.frog_toad:
            self.frog_toad.name = self.name_edit.text()
            self.frog_toad.breeding_season = self.breeding_edit.text()
            self.frog_toad.habitat = self.habitat_edit.text()
            self.frog_toad.diet = self.diet_edit.text()
            self.frog_toad.adult_size = self.size_edit.text()
            self.frog_toad.color_scheme = self.color_edit.text()
            self.frog_toad.profile_notes = self.notes_edit.toPlainText()
            self.frog_toad.images = [Image(image_path=path) for path in images]
            self.frog_toad.audio_files = [AudioFile(audio_path=path) for path in audio_files]
            if self.map_edit.text():
                if self.frog_toad.territory_map:
                    self.frog_toad.territory_map.map_path = self.map_edit.text()
                else:
                    self.frog_toad.territory_map = TerritoryMap(map_path=self.map_edit.text())
            self.frog_toad.states = [session.query(State).filter_by(state_name=state).first() for state in states]
            session.merge(self.frog_toad)
        else:
            frog_toad = FrogsToad(
                name=self.name_edit.text(),
                breeding_season=self.breeding_edit.text(),
                habitat=self.habitat_edit.text(),
                diet=self.diet_edit.text(),
                adult_size=self.size_edit.text(),
                color_scheme=self.color_edit.text(),
                profile_notes=self.notes_edit.toPlainText(),
                images=[Image(image_path=path) for path in images],
                audio_files=[AudioFile(audio_path=path) for path in audio_files],
                territory_map=TerritoryMap(map_path=self.map_edit.text()) if self.map_edit.text() else None,
                states=[session.query(State).filter_by(state_name=state).first() for state in states]
            )
            session.add(frog_toad)

        session.commit()
        session.close()
        self.accept()

class MapView(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        if self.engine:
            self.Session = sessionmaker(bind=self.engine)
        else:
            self.Session = None

        self.setWindowTitle("Interactive U.S. Map")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        layout = QVBoxLayout(self)

        self.webview = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge = MapBridge(self.engine, self, self.Session)
        self.channel.registerObject('bridge', self.bridge)
        self.webview.page().setWebChannel(self.channel)

        html = '''
        <html>
        <body style="background-color: #1E1E1E; margin: 0;">
        <object id="svgObject" type="image/svg+xml" data="us_map.svg" style="width: 100%; height: 400px;"></object>
        <script>
        var bridge;
        new QWebChannel(qt.webChannelTransport, function(channel) {
            bridge = channel.objects.bridge;
        });
        var svgObject = document.getElementById('svgObject');
        svgObject.addEventListener('load', function() {
            var svgDoc = svgObject.contentDocument;
            var paths = svgDoc.querySelectorAll('path');
            paths.forEach(function(path) {
                path.style.transition = "fill 0.3s";
                path.addEventListener('mouseover', function() {
                    path.style.fill = "#FF4500";
                });
                path.addEventListener('mouseout', function() {
                    path.style.fill = "";
                });
                path.addEventListener('click', function() {
                    bridge.stateClicked(path.id);
                });
            });
        });
        </script>
        </body>
        </html>
        '''
        self.webview.setHtml(html, QUrl.fromLocalFile(os.path.abspath('resources')))
        layout.addWidget(self.webview)

        self.species_list = QListWidget()
        self.species_list.setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #555;")
        layout.addWidget(self.species_list)

    def closeEvent(self, event):
        event.accept()

class MapBridge(QObject):
    def __init__(self, engine, map_view, Session=None):
        super().__init__()
        self.engine = engine
        self.map_view = map_view
        self.Session = Session

    @pyqtSlot(str)
    def stateClicked(self, state_id):
        if self.Session:
            session = self.Session()
            state = session.query(State).filter_by(state_name=state_id).first()
            if state:
                frogs_toads = state.frogs_toads
                self.map_view.species_list.clear()
                for ft in frogs_toads:
                    self.map_view.species_list.addItem(ft.name)
            session.close()
