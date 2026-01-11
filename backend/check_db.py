from app import app, db
from models import Dictionary, Phrase, Video, Alphabet

with app.app_context():
    print('=' * 50)
    print('DATABASE CONTENT CHECK')
    print('=' * 50)
    print(f'Dictionary entries: {Dictionary.query.count()}')
    print(f'Phrases: {Phrase.query.count()}')
    print(f'Videos: {Video.query.count()}')
    print(f'Alphabet letters: {Alphabet.query.count()}')
    print('=' * 50)
    
    if Dictionary.query.count() > 0:
        print('\nFirst 5 Dictionary words:')
        for word in Dictionary.query.limit(5):
            print(f'  - {word.nepali} ({word.romanized}) = {word.english}')
