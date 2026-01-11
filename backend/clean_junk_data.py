"""
Clean junk/test data from database
Removes XSS payloads, test data, and empty entries
"""
from app import app, db
from models import Dictionary, Phrase, Alphabet, Video

def clean_database():
    """Remove junk test data and XSS payloads"""
    with app.app_context():
        # Junk patterns to remove
        junk_patterns = [
            'AAAA',  # Long repeated characters
            'test',
            'Test',
            'TEST',
            '\'">',  # XSS payloads
            '<script',
            'javascript:',
            'onerror=',
            'onclick=',
        ]
        
        removed_count = 0
        
        # Clean Dictionary
        print("\n🔍 Checking Dictionary...")
        dict_words = Dictionary.query.all()
        for word in dict_words:
            # Check if empty or whitespace only
            if not word.nepali or not word.nepali.strip():
                print(f"  ❌ Removing empty word ID {word.id}")
                db.session.delete(word)
                removed_count += 1
                continue
            
            # Check if english is empty
            if not word.english or not word.english.strip():
                print(f"  ❌ Removing word with empty English ID {word.id}: '{word.nepali}'")
                db.session.delete(word)
                removed_count += 1
                continue
            
            # Check for junk patterns
            for pattern in junk_patterns:
                if (pattern.lower() in word.nepali.lower() or 
                    pattern.lower() in word.english.lower()):
                    print(f"  ❌ Removing junk word ID {word.id}: '{word.nepali}' / '{word.english}'")
                    db.session.delete(word)
                    removed_count += 1
                    break
            
            # Check for suspiciously long strings (over 100 chars of same letter)
            if len(word.nepali) > 50:
                unique_chars = len(set(word.nepali))
                if unique_chars < 3:  # Only 1-2 unique characters
                    print(f"  ❌ Removing suspicious long string ID {word.id}: '{word.nepali[:50]}...'")
                    db.session.delete(word)
                    removed_count += 1
        
        # Clean Phrases
        print("\n🔍 Checking Phrases...")
        phrase_list = Phrase.query.all()
        for phrase in phrase_list:
            # Check if empty
            if not phrase.nepali or not phrase.nepali.strip():
                print(f"  ❌ Removing empty phrase ID {phrase.id}")
                db.session.delete(phrase)
                removed_count += 1
                continue
            
            # Check for XSS payloads
            for pattern in junk_patterns:
                if (pattern in phrase.nepali or 
                    pattern in phrase.english or 
                    (phrase.romanized and pattern in phrase.romanized)):
                    print(f"  ❌ Removing junk/XSS phrase ID {phrase.id}: '{phrase.nepali}' / '{phrase.english}'")
                    db.session.delete(phrase)
                    removed_count += 1
                    break
        
        # Clean Alphabet (less likely to have junk, but check)
        print("\n🔍 Checking Alphabet...")
        alphabet_list = Alphabet.query.all()
        for letter in alphabet_list:
            if not letter.devanagari or not letter.devanagari.strip():
                print(f"  ❌ Removing empty letter ID {letter.id}")
                db.session.delete(letter)
                removed_count += 1
        
        # Commit changes
        if removed_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully removed {removed_count} junk entries!")
        else:
            print("\n✨ No junk data found - database is clean!")
        
        # Show remaining counts
        print(f"\n📊 Current Database Stats:")
        print(f"  • Dictionary: {Dictionary.query.count()} words")
        print(f"  • Phrases: {Phrase.query.count()} phrases")
        print(f"  • Alphabet: {Alphabet.query.count()} letters")
        print(f"  • Videos: {Video.query.count()} videos")

if __name__ == '__main__':
    print("🧹 Cleaning Database...")
    print("=" * 50)
    clean_database()
    print("=" * 50)
    print("✅ Database cleanup complete!")
