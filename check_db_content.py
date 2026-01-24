import sqlite3
import json

def check_latest_campaign():
    conn = sqlite3.connect('backend/ara_neuro_post.db')
    cursor = conn.cursor()
    
    # Get latest campaign
    cursor.execute('SELECT id, name, objective, status FROM campaigns ORDER BY id DESC LIMIT 1')
    campaign = cursor.fetchone()
    
    if not campaign:
        print("No campaigns found")
        return

    print(f"Campaign: {campaign}")
    campaign_id = campaign[0]
    
    # Get posts for this campaign
    cursor.execute('SELECT id, title, status FROM posts WHERE campaign_id = ?', (campaign_id,))
    posts = cursor.fetchall()
    
    print(f"Posts count: {len(posts)}")
    for post in posts:
        print(f" - {post}")
        
    conn.close()

if __name__ == "__main__":
    check_latest_campaign()
