class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Store the database credentials somewhere else
    SQLALCHEMY_DATABASE_URI = 'postgres://sid:sid12345@localhost:5432/flash_cards'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://sid:sid12345@localhost:5432/flash_cards'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True