"""
Clear all videos from the database to start fresh with correct links
"""
from database import db
from models import Video
from app import app

def clear_videos():
    with app.app_context():
        # Get count before
        count = Video.query.count()
        print(f"Found {count} videos in database")
        
        if count > 0:
            confirm = input(f"Delete all {count} videos? (yes/no): ")
            if confirm.lower() == 'yes':
                Video.query.delete()
                db.session.commit()
                print(f"✅ Deleted {count} videos successfully")
            else:
                print("❌ Cancelled")
        else:
            print("ℹ️ No videos to delete")

if __name__ == '__main__':
    clear_videos()
