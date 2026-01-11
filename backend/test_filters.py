"""Test dictionary filters"""
import requests

# Test colors
r = requests.get('http://localhost:5000/api/dictionary/', params={'category': 'colors', 'per_page': 100})
data = r.json()
print(f"Colors category: {len(data['words'])} words")
for w in data['words']:
    print(f"  • {w['nepali']} - {w['english']}")

print("\n" + "=" * 50 + "\n")

# Test alphabet
r = requests.get('http://localhost:5000/api/dictionary/', params={'category': 'alphabet', 'per_page': 100})
data = r.json()
print(f"Alphabet category: {len(data['words'])} words")
for w in data['words']:
    print(f"  • {w['nepali']} - {w['english']}")
