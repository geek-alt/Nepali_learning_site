"""
Migration script to add context and formality_level fields to Phrase table
"""
from app import app, db
from models import Phrase

def migrate():
    with app.app_context():
        print("🔄 Migrating Phrase table...")
        
        # Add columns if they don't exist
        try:
            # Try to access the new columns
            test = db.session.execute(db.text("SELECT context FROM phrase LIMIT 1"))
            print("✅ context column already exists")
        except Exception:
            print("➕ Adding context column...")
            db.session.execute(db.text("ALTER TABLE phrase ADD COLUMN context VARCHAR(200)"))
            db.session.commit()
            print("✅ context column added")
        
        try:
            test = db.session.execute(db.text("SELECT formality_level FROM phrase LIMIT 1"))
            print("✅ formality_level column already exists")
        except Exception:
            print("➕ Adding formality_level column...")
            db.session.execute(db.text("ALTER TABLE phrase ADD COLUMN formality_level VARCHAR(20) DEFAULT 'casual'"))
            db.session.commit()
            print("✅ formality_level column added")
        
        # Update existing phrases with default values
        print("\n🔄 Updating existing phrases...")
        phrases = Phrase.query.all()
        for phrase in phrases:
            if not hasattr(phrase, 'formality_level') or phrase.formality_level is None:
                phrase.formality_level = 'casual'
        
        db.session.commit()
        print(f"✅ Updated {len(phrases)} phrases")
        
        print("\n🎉 Migration complete!")

if __name__ == '__main__':
    migrate()
