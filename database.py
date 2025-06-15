import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtSvg import QSvgWidget
import pydub
import os

def init_db(db_path):
    # Use db_path to initialize the database
    # Example with SQLite:
    import sqlite3
    conn = sqlite3.connect(db_path)
    # Add your initialization code here
    return conn  # or whatever your engine needs to be
    c.execute('''CREATE TABLE IF NOT EXISTS FrogsToads (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        BreedingSeason TEXT,
        Habitat TEXT,
        Diet TEXT,
        AdultSize TEXT,
        ColorScheme TEXT,
        ProfileNotes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Images (
        ID INTEGER PRIMARY KEY,
        FrogToadID INTEGER,
        ImagePath TEXT,
        FOREIGN KEY(FrogToadID) REFERENCES FrogsToads(ID))''')
    c.execute('''CREATE TABLE IF NOT EXISTS AudioFiles (
        ID INTEGER PRIMARY KEY,
        FrogToadID INTEGER,
        AudioPath TEXT,
        FOREIGN KEY(FrogToadID) REFERENCES FrogsToads(ID))''')
    c.execute('''CREATE TABLE IF NOT EXISTS TerritoryMaps (
        ID INTEGER PRIMARY KEY,
        FrogToadID INTEGER,
        MapPath TEXT,
        FOREIGN KEY(FrogToadID) REFERENCES FrogsToads(ID))''')
    c.execute('''CREATE TABLE IF NOT EXISTS States (
        ID INTEGER PRIMARY KEY,
        StateName TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS FrogToadStates (
        FrogToadID INTEGER,
        StateID INTEGER,
        FOREIGN KEY(FrogToadID) REFERENCES FrogsToads(ID),
        FOREIGN KEY(StateID) REFERENCES States(ID))''')
    conn.commit()
    conn.close()

# Main GUI
class FrogToadApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frog & Toad Database")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Species list
        self.species_list = QListWidget()
        layout.addWidget(self.species_list)

        # Buttons
        self.edit_button = QPushButton("Edit Profile")
        self.map_button = QPushButton("View Map")
        layout.addWidget(self.edit_button)
        layout.addWidget(self.map_button)

        # Connect buttons
        self.map_button.clicked.connect(self.show_map)

    def show_map(self):
        # SVG map display (assumes us_map.svg exists)
        map_window = QWidget()
        map_layout = QVBoxLayout(map_window)
        svg_widget = QSvgWidget("us_map.svg")
        map_layout.addWidget(svg_widget)
        map_window.show()

# Run the app
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = FrogToadApp()
    window.show()
    sys.exit(app.exec_())
