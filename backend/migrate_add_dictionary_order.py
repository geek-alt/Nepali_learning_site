"""
Migration script to add order_index field to Dictionary table
"""
from app import app, db
from models import Dictionary

def migrate():
    with app.app_context():
        print("🔄 Migrating Dictionary table...")
        
        # Add column if it doesn't exist
        try:
            # Try to access the new column
            test = db.session.execute(db.text("SELECT order_index FROM dictionary LIMIT 1"))
            print("✅ order_index column already exists")
        except Exception:
            print("➕ Adding order_index column...")
            db.session.execute(db.text("ALTER TABLE dictionary ADD COLUMN order_index INTEGER"))
            db.session.commit()
            print("✅ order_index column added")
        
        # Update existing entries with sequential order
        print("\n🔄 Setting initial order for existing entries...")
        words = Dictionary.query.order_by(Dictionary.id).all()
        for idx, word in enumerate(words, start=1):
            if not hasattr(word, 'order_index') or word.order_index is None:
                word.order_index = idx
        
        db.session.commit()
        print(f"✅ Set order for {len(words)} dictionary entries")
        
        print("\n🎉 Migration complete!")

if __name__ == '__main__':
    migrate()
