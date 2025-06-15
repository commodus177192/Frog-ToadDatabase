import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from views import FrogsMainWindow
from PyQt5.QtWidgets import QApplication

def init_db(db_path):
    """Set up the database engine and create tables if they don’t exist."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db_path = "frogs_toads.db"
    engine = init_db(db_path)
    window = FrogsMainWindow(engine=engine)
    window.show()
    sys.exit(app.exec_())
