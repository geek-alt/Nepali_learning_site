# नेपाली सिकौं - V2 Implementation Guide

## Quick Start for Adding Content

This guide shows you how to easily add Dictionary words, YouTube videos, and PDFs to your platform using the Admin Panel.

---

## 📚 Method 1: Adding Dictionary Words

### Via Admin Panel (Easiest)
1. Open admin at `http://127.0.0.1:5000/admin`
2. Click "Manage Dictionary" tab
3. Click "+ Add New Word"
4. Fill in the form:
   - **Nepali Text**: नेपाली (required)
   - **Romanized**: nepali (required)
   - **English**: English translation (required)
   - **Part of Speech**: noun, verb, adjective, etc.
   - **Usage Example**: English example sentence
   - **Nepali Example**: नेपाली उदाहरण
   - **Difficulty**: 1 (Beginner), 2 (Intermediate), 3 (Advanced)
   - **Category**: nature, food, animals, daily, business, etc.
5. Click "Save Word"

### Via API (Programmatic)
```bash
curl -X POST http://127.0.0.1:5000/api/dictionary \
  -H "Content-Type: application/json" \
  -d '{
    "nepali": "पानी",
    "romanized": "pani",
    "english": "water",
    "part_of_speech": "noun",
    "category": "nature",
    "difficulty": 1,
    "usage_example": "Drink water to stay hydrated",
    "nepali_example": "मलाई पानी चाहिन्छ"
  }'
```

### Via CSV Bulk Import (Fastest for Many Words)
Prepare a CSV file with headers:
```
nepali,romanized,english,part_of_speech,category,difficulty
पानी,pani,water,noun,nature,1
खान,khana,eat,verb,food,1
घर,ghar,house,noun,building,1
किताब,kitaab,book,noun,education,1
```

Save as `words.csv`, then use API:
```bash
curl -X POST http://127.0.0.1:5000/api/dictionary/bulk-import \
  -H "Content-Type: application/json" \
  -d '{
    "words": [
      {"nepali": "पानी", "romanized": "pani", "english": "water", "part_of_speech": "noun", "category": "nature", "difficulty": 1},
      {"nepali": "खान", "romanized": "khana", "english": "eat", "part_of_speech": "verb", "category": "food", "difficulty": 1}
    ]
  }'
```

### Search Dictionary
Users can search on the main site:
```
GET /api/dictionary/search?q=water
GET /api/dictionary/search?q=पानी
GET /api/dictionary/category/nature
GET /api/dictionary/difficulty/1
```

---

## 🎬 Method 2: Adding YouTube Videos

### Step 1: Get YouTube Video ID
From URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
The video ID is: `dQw4w9WgXcQ`

### Step 2: Add to Admin Panel
1. Go to admin dashboard
2. Click "Manage Videos" tab
3. Click "+ Add New Video"
4. Fill in:
   - **Title**: "Learn Nepali Basics with Aarav"
   - **YouTube ID**: dQw4w9WgXcQ
   - **Category**: alphabet, phrases, grammar, culture, etc.
   - **Difficulty**: 1-3
   - **Description**: What the video teaches
   - **Duration**: 630 (in seconds)
   - **Transcript**: (optional) Video transcript for searching
   - **Notes**: Learning points from video
5. Click "Save Video"

### Step 3: Organize into Playlists (Optional)
1. Create playlists: "Beginner Series", "Grammar Lesson 1", etc.
2. Add videos to playlists
3. Users can browse by playlist

### Via API
```bash
# Create a playlist
curl -X POST http://127.0.0.1:5000/api/resources/playlists \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beginner Nepali Lessons",
    "description": "Start here for basics",
    "category": "beginner",
    "difficulty": 1
  }'

# Add video to playlist
curl -X POST http://127.0.0.1:5000/api/resources/videos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Nepali Alphabet",
    "youtube_id": "dQw4w9WgXcQ",
    "playlist_id": 1,
    "category": "alphabet",
    "difficulty": 1,
    "duration": 630,
    "description": "Complete guide to Devanagari script"
  }'
```

---

## 📄 Method 3: Adding PDF Resources

### Prepare Your PDF
1. Create a PDF document (worksheet, guide, reference sheet)
2. Save it as: `worksheet_numbers.pdf`
3. Place in: `site/frontend/static/pdfs/`

### Step 2: Add to Admin Panel
1. Go to admin > "Manage Resources"
2. Click "+ Add New Resource"
3. Select file type: "PDF"
4. Fill in:
   - **Title**: "Nepali Numbers 1-100 Worksheet"
   - **Category**: worksheet, guide, reference
   - **Description**: What's in the PDF
   - **Difficulty**: 1-3
   - **Tags**: numbers, beginner, counting, practice
5. Upload file
6. System generates preview automatically
7. Click "Save Resource"

### PDF Features
- ✅ Auto-generates preview of first page
- ✅ Shows page count, file size
- ✅ Tracks download count
- ✅ Searchable by tags/title
- ✅ Downloadable with one click
- ✅ Beautiful preview modal

### Via API
```bash
curl -X POST http://127.0.0.1:5000/api/resources/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nepali Numbers Worksheet",
    "description": "Practice counting 1-100",
    "category": "worksheet",
    "file_path": "/static/pdfs/numbers.pdf",
    "pages": 3,
    "file_size": 2048000,
    "difficulty": 1,
    "tags": "numbers, counting, practice"
  }'
```

---

## 🎨 Content Organization Tips

### Dictionary Words - Best Practices
- Add 5-10 new words per week
- Organize by categories:
  - **Daily Words**: common, greetings, food, family
  - **Nature**: animals, plants, weather, environment
  - **Business**: work, office, money, trade
  - **Academic**: education, science, math, history
  - **Cultural**: festivals, traditions, customs
- Include usage examples for context
- Gradual difficulty levels

### Videos - Curation Tips
- Source from reputable Nepali learning YouTube channels
- Organize by skill level:
  - Beginner: Alphabet, numbers, greetings
  - Intermediate: Conversations, grammar
  - Advanced: News, documentaries, interviews
- Create playlists for learning paths:
  - "Week 1: Introduction"
  - "Week 2: Alphabet Mastery"
  - "Week 3: Common Phrases"
- Add timestamps in transcript for key moments

### PDFs - Resource Types
- **Worksheets**: Practice exercises with answer keys
- **Study Guides**: Detailed grammar, pronunciation rules
- **Reference Sheets**: Quick lookup tables, cheat sheets
- **Printables**: Flash cards, posters, wall charts
- **Mock Tests**: Assessment materials

---

## 🔍 Content Discovery Features

### Users can find content by:

**Dictionary**
```
/api/dictionary/search?q=water
/api/dictionary/category/food
/api/dictionary/difficulty/1
/api/dictionary/trending
```

**Videos**
```
/api/resources/videos?category=alphabet
/api/resources/playlists
/api/resources/videos/trending
```

**PDFs**
```
/api/resources/pdf?category=worksheet
/api/resources/pdf?difficulty=1
/api/resources/pdf/categories
```

---

## 📊 Content Statistics

Your platform tracks:
- **Dictionary**: Word views, most popular words
- **Videos**: View count, completion rate
- **PDFs**: Download count, user engagement

Check admin dashboard for analytics!

---

## 🎯 Growth Plan

### Month 1
- Add 100 basic dictionary words
- Create 10 YouTube playlists
- Add 20 beginner worksheets
- Total: 130+ content items

### Month 2
- Expand dictionary to 300 words
- Add 20 more video playlists
- Add 30 advanced resources
- Total: 350+ content items

### Month 3+
- Target 1000+ dictionary words
- 50+ video playlists (500+ videos)
- 100+ downloadable PDFs
- Complete learning ecosystem!

---

## 💡 Content Strategy Examples

### "Learn Daily" Path
1. Monday: Learn 2-3 new words (dictionary)
2. Tuesday: Watch pronunciation video (5-10 min)
3. Wednesday: Practice with worksheet PDF
4. Thursday: Learn phrases using words
5. Friday: Review with quiz

### "Video First" Path
1. Watch themed playlist (alphabet, food, etc.)
2. Review transcript for new words
3. Look up words in dictionary
4. Download reference sheet PDF
5. Complete worksheet

### "Gamified" Path (Future)
1. Complete dictionary challenge (learn 10 words)
2. Earn badge
3. Watch video lesson
4. Complete worksheet
5. Unlock next level
6. Get achievement certificate (PDF)

---

## 🚀 Coming Soon Features

- **User Accounts**: Save progress, track learning
- **Pronunciation Audio**: Add audio files for words
- **Video Transcripts**: Full searchable transcripts
- **Interactive Quizzes**: Test knowledge
- **Offline Content**: Download for offline study
- **Mobile App**: iOS/Android versions
- **Community**: Forum for questions

---

## 📱 Responsive Design

All content displays beautifully on:
- ✅ Desktop (1920px+)
- ✅ Tablets (768px-1024px)
- ✅ Mobile phones (320px-767px)

Content automatically adjusts layout!

---

## 🔐 Admin Security

- Admin panel requires authentication (coming soon)
- All uploads validated
- File type checking
- Size limits enforced
- Suspicious content flagged

---

## 💬 Need Help?

### API Documentation
- GET all words: `/api/dictionary`
- Search: `/api/dictionary/search?q=test`
- Create word: POST `/api/dictionary`
- Get videos: `/api/resources/videos`
- Get PDFs: `/api/resources/pdf`

### Browser Errors?
- Check Flask server is running
- Verify database tables created
- Check static file paths
- Review browser console for errors

---

## ✨ Pro Tips

1. **Add Rich Content**: Include examples, audio, references
2. **Organize Well**: Use clear categories and tags
3. **Track Progress**: Monitor what's popular
4. **Update Regularly**: Fresh content keeps users engaged
5. **Gather Feedback**: Ask users what they want to learn

---

**Your platform is now ready to grow! Start adding content today!** 🎉
