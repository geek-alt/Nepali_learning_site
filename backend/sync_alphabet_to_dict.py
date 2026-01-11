"""
Sync Alphabet table to Dictionary table
Creates dictionary entries for all alphabet letters
"""
from app import app, db
from models import Alphabet, Dictionary

def sync_alphabet_to_dictionary():
    """Copy all alphabet letters to dictionary with category='alphabet'"""
    with app.app_context():
        print("🔄 Syncing Alphabet table to Dictionary...")
        print("=" * 60)
        
        # Get all alphabet letters
        alphabet_letters = Alphabet.query.order_by(Alphabet.order_index).all()
        print(f"Found {len(alphabet_letters)} letters in Alphabet table")
        
        # Check existing dictionary entries with category='alphabet'
        existing_dict = {d.nepali: d for d in Dictionary.query.filter_by(category='alphabet').all()}
        print(f"Found {len(existing_dict)} existing alphabet entries in Dictionary")
        
        added = 0
        updated = 0
        skipped = 0
        
        for letter in alphabet_letters:
            # Check if already exists in dictionary by nepali text (across ALL categories due to unique constraint)
            existing = Dictionary.query.filter_by(nepali=letter.devanagari).first()
            
            if existing and existing.category == 'alphabet':
                # Already in alphabet category, update if needed
                if existing.romanized != letter.romanized or existing.english != (letter.pronunciation or f"{letter.type} - {letter.sound}"):
                    existing.romanized = letter.romanized
                    existing.english = letter.pronunciation or f"{letter.type} - {letter.sound}"
                    existing.usage_example = f"This is the letter '{letter.romanized}' ({letter.sound})"
                    existing.audio_url = letter.audio_url
                    updated += 1
                    print(f"  ✏️ Updated: {letter.devanagari} ({letter.romanized})")
                else:
                    skipped += 1
            elif existing:
                # Exists in a different category - skip due to unique constraint
                skipped += 1
                print(f"  ⏭️ Skipped: {letter.devanagari} ({letter.romanized}) - already exists as '{existing.category}'")
            else:
                # Create new dictionary entry
                new_entry = Dictionary(
                    nepali=letter.devanagari,
                    romanized=letter.romanized,
                    english=letter.pronunciation or f"{letter.type} - {letter.sound}",
                    part_of_speech='letter',
                    category='alphabet',
                    difficulty=1,  # All alphabet is beginner level
                    usage_example=f"This is the letter '{letter.romanized}' ({letter.sound})",
                    audio_url=letter.audio_url
                )
                db.session.add(new_entry)
                added += 1
                print(f"  ✅ Added: {letter.devanagari} ({letter.romanized}) - {letter.pronunciation or letter.sound}")
        
        # Commit all changes
        if added > 0 or updated > 0:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"✅ Sync Complete!")
            print(f"   Added: {added} new entries")
            print(f"   Updated: {updated} entries")
            print(f"   Skipped: {skipped} (already up-to-date)")
            print(f"   Total in Dictionary (alphabet): {Dictionary.query.filter_by(category='alphabet').count()}")
        else:
            print("\n✨ All alphabet entries are already synced!")
        
        print("=" * 60)

if __name__ == '__main__':
    sync_alphabet_to_dictionary()
