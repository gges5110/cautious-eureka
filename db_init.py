import models

def init():
  engine = models.db.get_engine()
  if not engine.dialect.has_table(engine, 'user_table'):
    # Create method: http://docs.sqlalchemy.org/en/latest/core/metadata.html?highlight=create#sqlalchemy.schema.Table.create
    # Usage: https://stackoverflow.com/a/34240889
    models.User.__table__.create(engine)
    print('User table did not exist, creating...')

  if not engine.dialect.has_table(engine, 'deck_table'):
    models.Deck.__table__.create(engine)
    print('Deck table did not exist, creating...')

if __name__ == '__main__':
  init()