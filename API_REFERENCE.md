# नेपाली सिकौं - V2 API Reference

Complete API documentation for dictionary, videos, and PDF resources.

## Base URL
```
http://127.0.0.1:5000/api
```

---

## 📚 Dictionary Endpoints

### Get All Words
```
GET /dictionary
GET /dictionary?page=1&per_page=20&difficulty=1&category=food
```
**Response:**
```json
{
  "words": [
    {
      "id": 1,
      "nepali": "पानी",
      "romanized": "pani",
      "english": "water",
      "part_of_speech": "noun",
      "difficulty": 1,
      "category": "nature",
      "audio_url": "/static/audio/pani.mp3",
      "views": 45
    }
  ],
  "total": 350,
  "pages": 18,
  "current_page": 1
}
```

### Get Single Word
```
GET /dictionary/<id>
```
**Response:**
```json
{
  "id": 1,
  "nepali": "पानी",
  "romanized": "pani",
  "english": "water",
  "part_of_speech": "noun",
  "usage_example": "Drink water to stay healthy",
  "nepali_example": "मलाई पानी चाहिन्छ",
  "audio_url": "/static/audio/pani.mp3",
  "difficulty": 1,
  "category": "nature",
  "synonyms": "जल",
  "antonyms": null,
  "views": 45
}
```

### Create Word
```
POST /dictionary
Content-Type: application/json

{
  "nepali": "पानी",
  "romanized": "pani",
  "english": "water",
  "part_of_speech": "noun",
  "usage_example": "Drink water",
  "nepali_example": "पानी पिउ",
  "difficulty": 1,
  "category": "nature",
  "synonyms": "जल"
}
```
**Response:** `201 Created`

### Update Word
```
PUT /dictionary/<id>
Content-Type: application/json

{
  "english": "water (clear liquid)",
  "usage_example": "Pure water is essential"
}
```
**Response:** `200 OK`

### Delete Word
```
DELETE /dictionary/<id>
```
**Response:** `204 No Content`

### Search Words
```
GET /dictionary/search?q=water
GET /dictionary/search?q=पानी
GET /dictionary/search?q=pani&category=nature&difficulty=1
```
**Response:**
```json
[
  {
    "id": 1,
    "nepali": "पानी",
    "romanized": "pani",
    "english": "water",
    "category": "nature",
    "difficulty": 1
  }
]
```

### Get Categories
```
GET /dictionary/categories
```
**Response:**
```json
["nature", "food", "animals", "business", "daily", "education"]
```

### Get by Category
```
GET /dictionary/category/food?page=1&per_page=20
```

### Get by Difficulty
```
GET /dictionary/difficulty/1?page=1&per_page=20
```

### Get Trending Words
```
GET /dictionary/trending
```
Most viewed/popular words

### Bulk Import
```
POST /dictionary/bulk-import
Content-Type: application/json

{
  "words": [
    {
      "nepali": "पानी",
      "romanized": "pani",
      "english": "water",
      "part_of_speech": "noun",
      "category": "nature",
      "difficulty": 1
    },
    {
      "nepali": "खान",
      "romanized": "khana",
      "english": "eat",
      "part_of_speech": "verb",
      "category": "food",
      "difficulty": 1
    }
  ]
}
```
**Response:**
```json
{
  "success": true,
  "added": 2,
  "errors": []
}
```

---

## 🎬 Video Endpoints

### Get All Videos
```
GET /resources/videos
GET /resources/videos?page=1&per_page=12&category=alphabet&difficulty=1
```
**Response:**
```json
{
  "videos": [
    {
      "id": 1,
      "title": "Learn Nepali Alphabet",
      "youtube_id": "dQw4w9WgXcQ",
      "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg",
      "duration": 630,
      "category": "alphabet",
      "difficulty": 1,
      "view_count": 234
    }
  ],
  "total": 45,
  "pages": 4
}
```

### Get Single Video
```
GET /resources/videos/<id>
```
**Response:**
```json
{
  "id": 1,
  "title": "Learn Nepali Alphabet",
  "description": "Complete guide to Devanagari script",
  "youtube_id": "dQw4w9WgXcQ",
  "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg",
  "category": "alphabet",
  "difficulty": 1,
  "transcript": "Hello, today we'll learn the Nepali alphabet...",
  "notes": "Key points:\n- 36 consonants\n- 12 vowels\n- Write from left to right",
  "view_count": 234
}
```

### Create Video
```
POST /resources/videos
Content-Type: application/json

{
  "title": "Learn Nepali Alphabet",
  "description": "Complete guide to Devanagari script",
  "youtube_id": "dQw4w9WgXcQ",
  "duration": 630,
  "category": "alphabet",
  "difficulty": 1,
  "transcript": "Full video transcript here...",
  "notes": "Key learning points..."
}
```

### Update Video
```
PUT /resources/videos/<id>
Content-Type: application/json

{
  "notes": "Updated learning points..."
}
```

### Delete Video
```
DELETE /resources/videos/<id>
```

### Get Trending Videos
```
GET /resources/videos/trending
```

### Get Playlists
```
GET /resources/playlists
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Beginner Series",
    "description": "Start your Nepali journey here",
    "category": "beginner",
    "thumbnail_url": "...",
    "video_count": 12,
    "difficulty": 1
  }
]
```

### Create Playlist
```
POST /resources/playlists
Content-Type: application/json

{
  "name": "Beginner Series",
  "description": "Start your Nepali journey",
  "category": "beginner",
  "difficulty": 1
}
```

---

## 📄 PDF Resource Endpoints

### Get All PDFs
```
GET /resources/pdf
GET /resources/pdf?page=1&per_page=12&category=worksheet&difficulty=1
```
**Response:**
```json
{
  "pdfs": [
    {
      "id": 1,
      "title": "Nepali Numbers 1-100 Worksheet",
      "description": "Practice counting with exercises",
      "category": "worksheet",
      "preview_url": "/static/pdfs/numbers_preview.jpg",
      "pages": 3,
      "file_size": 2048000,
      "difficulty": 1,
      "downloads": 45,
      "created_at": "2026-01-09T10:30:00"
    }
  ],
  "total": 28,
  "pages": 3
}
```

### Get Single PDF
```
GET /resources/pdf/<id>
```
**Response:**
```json
{
  "id": 1,
  "title": "Nepali Numbers Worksheet",
  "description": "Practice counting 1-100 with exercises",
  "category": "worksheet",
  "file_path": "/static/pdfs/numbers.pdf",
  "preview_url": "/static/pdfs/numbers_preview.jpg",
  "pages": 3,
  "file_size": 2048000,
  "difficulty": 1,
  "downloads": 45,
  "tags": "numbers, counting, practice"
}
```

### Create PDF
```
POST /resources/pdf
Content-Type: application/json

{
  "title": "Nepali Numbers Worksheet",
  "description": "Practice counting 1-100",
  "category": "worksheet",
  "file_path": "/static/pdfs/numbers.pdf",
  "preview_url": "/static/pdfs/numbers_preview.jpg",
  "pages": 3,
  "file_size": 2048000,
  "difficulty": 1,
  "tags": "numbers, counting, practice"
}
```

### Update PDF
```
PUT /resources/pdf/<id>
Content-Type: application/json

{
  "description": "Updated description"
}
```

### Delete PDF
```
DELETE /resources/pdf/<id>
```

### Download PDF (Track Download)
```
GET /resources/pdf/<id>/download
```
**Response:**
```json
{
  "file_path": "/static/pdfs/numbers.pdf",
  "title": "Nepali Numbers Worksheet",
  "downloads": 46
}
```

### Get PDF Categories
```
GET /resources/pdf/categories
```
**Response:**
```json
["worksheet", "guide", "reference", "flashcard", "poster"]
```

---

## 🔄 Generic Resources Endpoints

### Get All Resources
```
GET /resources
GET /resources?page=1&per_page=12&type=pdf&category=worksheet
```

### Create Resource
```
POST /resources
Content-Type: application/json

{
  "title": "Resource Title",
  "description": "Description here",
  "resource_type": "pdf|guide|tips|worksheet",
  "category": "category_name",
  "file_url": "/static/files/...",
  "thumbnail_url": "/static/images/...",
  "difficulty": 1
}
```

### Get Resource
```
GET /resources/<id>
```

### Update Resource
```
PUT /resources/<id>
```

### Delete Resource
```
DELETE /resources/<id>
```

### Get Categories
```
GET /resources/categories
```

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| 200  | Success - Request successful |
| 201  | Created - Resource created |
| 204  | No Content - Deletion successful |
| 400  | Bad Request - Invalid data |
| 404  | Not Found - Resource not found |
| 500  | Server Error - Something went wrong |

---

## 🔗 Frontend Integration Examples

### Add Word to Dictionary
```javascript
async function addWord(wordData) {
  const response = await fetch('/api/dictionary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(wordData)
  });
  return response.json();
}

// Usage
addWord({
  nepali: 'पानी',
  romanized: 'pani',
  english: 'water',
  part_of_speech: 'noun',
  category: 'nature',
  difficulty: 1
});
```

### Search Dictionary
```javascript
async function searchDictionary(query) {
  const response = await fetch(`/api/dictionary/search?q=${query}`);
  return response.json();
}
```

### Embed YouTube Video
```javascript
function embedVideo(youtubeId) {
  return `<iframe width="100%" height="400" 
    src="https://www.youtube.com/embed/${youtubeId}" 
    frameborder="0" allowfullscreen></iframe>`;
}
```

### Download PDF
```javascript
async function downloadPDF(pdfId) {
  const response = await fetch(`/api/resources/pdf/${pdfId}/download`);
  const data = await response.json();
  window.location.href = data.file_path;
}
```

---

## 🎯 Common Queries

### Get beginner dictionary words
```
GET /api/dictionary?difficulty=1&per_page=50
```

### Search for food words
```
GET /api/dictionary/search?q=food&category=food
```

### Get alphabet videos
```
GET /api/resources/videos?category=alphabet&difficulty=1
```

### Get all worksheets
```
GET /api/resources/pdf?category=worksheet
```

### Get trending content
```
GET /api/dictionary/trending
GET /api/resources/videos/trending
```

---

## 🚀 Performance Tips

- Use pagination: `?page=1&per_page=20`
- Cache results in frontend
- Search with category filter for faster results
- Limit trending queries to top 10-20

---

## 📝 Notes

- All timestamps use ISO 8601 format
- Views/downloads are auto-incremented
- Deleted content cannot be recovered
- Bulk imports validate data before saving
- Search is case-insensitive

---

**Last Updated:** January 9, 2026
**API Version:** 2.0
