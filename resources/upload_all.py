import requests
import os

# Base URL
BASE_URL = 'http://localhost:5000/api/bulk'

# Resource directory
RESOURCE_DIR = r'c:\Users\bhand\Desktop\Codefolder\site\resources'

def upload_file(resource_type, filename):
    """Upload a CSV file to the bulk upload endpoint"""
    filepath = os.path.join(RESOURCE_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filename}")
        return
    
    print(f"\n📤 Uploading {filename}...")
    print(f"   Type: {resource_type}")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/{resource_type}', files=files)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                print(f"   📊 Added: {data.get('added', 0)}")
                print(f"   ⚠️  Skipped: {data.get('skipped', 0)}")
                if data.get('errors'):
                    print(f"   ❌ Errors: {len(data['errors'])}")
                    for err in data['errors'][:3]:  # Show first 3 errors
                        print(f"      • {err}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   {response.text}")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def main():
    print("=" * 60)
    print("🚀 BULK UPLOAD RESOURCES TO NEPALI LEARNING SITE")
    print("=" * 60)
    
    # Upload dictionary
    upload_file('dictionary', 'dictionary_100_words.csv')
    
    # Upload phrases
    upload_file('phrases', 'phrases_100.csv')
    
    # Upload alphabet
    upload_file('alphabet', 'complete_alphabet.csv')
    
    # Upload videos
    upload_file('videos', 'youtube_videos_20.csv')
    
    print("\n" + "=" * 60)
    print("✅ UPLOAD COMPLETE!")
    print("=" * 60)
    print("\n📊 Summary:")
    print("   • 100+ Dictionary words added")
    print("   • 100 Survival phrases added")
    print("   • 48 Alphabet letters added")
    print("   • 20 YouTube videos added")
    print("\n🌐 Visit: http://localhost:5000/admin")
    print("   Click '📤 Bulk Upload' to see results")

if __name__ == '__main__':
    main()
