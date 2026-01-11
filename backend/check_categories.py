"""Check categories in database"""
from app import app, db
from models import Dictionary, Phrase

with app.app_context():
    print("📊 Dictionary Categories:")
    print("=" * 50)
    dict_categories = db.session.query(Dictionary.category, db.func.count(Dictionary.id)).group_by(Dictionary.category).all()
    total_dict = Dictionary.query.count()
    print(f"Total dictionary words: {total_dict}\n")
    
    for cat, count in dict_categories:
        print(f"  • {cat or '(None)'}: {count} words")
    
    print("\n" + "=" * 50)
    print("📊 Phrase Categories:")
    print("=" * 50)
    phrase_categories = db.session.query(Phrase.category, db.func.count(Phrase.id)).group_by(Phrase.category).all()
    total_phrases = Phrase.query.count()
    print(f"Total phrases: {total_phrases}\n")
    
    for cat, count in phrase_categories:
        print(f"  • {cat or '(None)'}: {count} phrases")
