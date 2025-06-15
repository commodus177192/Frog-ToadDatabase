from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship  # Updated import

# Create the base class for all database models
Base = declarative_base()

# Junction table for the many-to-many relationship between FrogsToads and States
# This links each species to the states where it’s native
frog_toad_states = Table(
    'frog_toad_states',
    Base.metadata,
    Column('frog_toad_id', Integer, ForeignKey('frogs_toads.id')),
    Column('state_id', Integer, ForeignKey('states.id'))
)

# Main entity for frog and toad species, storing all core profile data
class FrogsToad(Base):
    __tablename__ = 'frogs_toads'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    breeding_season = Column(String)
    habitat = Column(String)
    diet = Column(String)
    adult_size = Column(String)
    color_scheme = Column(String)
    profile_notes = Column(String)
    # Add any other columns or relationships your app needs

    # Relationships to other tables
    # One-to-many with images (a species can have multiple images)
    images = relationship('Image', back_populates='frog_toad')
    # One-to-many with audio files (multiple calls per species)
    audio_files = relationship('AudioFile', back_populates='frog_toad')
    # One-to-one with territory map (one map per species)
    territory_map = relationship('TerritoryMap', uselist=False, back_populates='frog_toad')
    # Many-to-many with states (species can be native to multiple states)
    states = relationship('State', secondary=frog_toad_states, back_populates='frogs_toads')

# Table for storing image file paths associated with each species
class Image(Base):
    __tablename__ = 'images'

    # Unique identifier for each image
    id = Column(Integer, primary_key=True)
    # Links this image to a specific frog/toad species
    frog_toad_id = Column(Integer, ForeignKey('frogs_toads.id'))
    # Path to the image file on disk (e.g., "data/images/bullfrog1.jpg")
    image_path = Column(String)

    # Relationship back to the FrogsToad entity
    frog_toad = relationship('FrogsToad', back_populates='images')

# Table for storing audio file paths (e.g., frog calls)
class AudioFile(Base):
    __tablename__ = 'audio_files'

    # Unique identifier for each audio file
    id = Column(Integer, primary_key=True)
    # Links this audio to a specific frog/toad species
    frog_toad_id = Column(Integer, ForeignKey('frogs_toads.id'))
    # Path to the audio file on disk (e.g., "data/audio/bullfrog_call.mp3")
    audio_path = Column(String)

    # Relationship back to the FrogsToad entity
    frog_toad = relationship('FrogsToad', back_populates='audio_files')

# Table for storing territory map image paths
class TerritoryMap(Base):
    __tablename__ = 'territory_maps'

    # Unique identifier for each map
    id = Column(Integer, primary_key=True)
    # Links this map to a specific frog/toad species
    frog_toad_id = Column(Integer, ForeignKey('frogs_toads.id'))
    # Path to the map image on disk (e.g., "data/maps/bullfrog_range.jpg")
    map_path = Column(String)

    # Relationship back to the FrogsToad entity
    frog_toad = relationship('FrogsToad', back_populates='territory_map')

# Table for storing U.S. state names
class State(Base):
    __tablename__ = 'states'

    # Unique identifier for each state
    id = Column(Integer, primary_key=True)
    # Name of the state (e.g., "California")
    state_name = Column(String)

    # Many-to-many relationship back to FrogsToad
    frogs_toads = relationship('FrogsToad', secondary=frog_toad_states, back_populates='states')
