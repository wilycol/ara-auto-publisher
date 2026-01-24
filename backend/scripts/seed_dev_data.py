import sys
import os
import uuid
from sqlalchemy.orm import Session
# Ensure we can import app modules by adding backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Project, Campaign, Post, ContentStatus

def seed_dev_data():
    print("🌱 [SEED DEV] Starting seeding process for DEV environment...")
    
    # 1. Get Target User ID (Supabase Auth UUID)
    # Since we cannot create auth users via SQL without admin rights easily,
    # we ask the user to provide an existing User ID from their Supabase Dashboard.
    target_user_id = os.getenv("SEED_USER_ID")
    if not target_user_id:
        print("\n⚠️  MISSING SEED_USER_ID")
        print("   Please create a user in Supabase Auth (Authentication -> Users -> Add User).")
        print("   Then, copy their User UID and run this script as:")
        print("   $ env SEED_USER_ID=your-uuid-here python scripts/seed_dev_data.py")
        return

    db = SessionLocal()
    try:
        # 2. Check/Create Project
        print(f"👉 Checking project for User {target_user_id}...")
        project = db.query(Project).filter(Project.owner_id == target_user_id).first()
        if not project:
            print("   Creating new Project 'ARA Demo Project'...")
            project = Project(
                name="ARA Demo Project",
                description="Project created by seed script for DEV testing",
                owner_id=target_user_id
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            print(f"   ✅ Project Created: ID {project.id}")
        else:
            print(f"   ℹ️  Project already exists: ID {project.id}")

        # 3. Check/Create Campaign
        print("👉 Checking campaign...")
        campaign = db.query(Campaign).filter(Campaign.project_id == project.id).first()
        if not campaign:
            print("   Creating new Campaign 'Launch MVP'...")
            campaign = Campaign(
                project_id=project.id,
                name="Launch MVP",
                objective="brand_awareness",
                tone="professional",
                status="active"
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            print(f"   ✅ Campaign Created: ID {campaign.id}")
        else:
            print(f"   ℹ️  Campaign already exists: ID {campaign.id}")

        # 4. Create Posts (Always add a few fresh ones if less than 3)
        print("👉 Checking posts...")
        post_count = db.query(Post).filter(Post.campaign_id == campaign.id).count()
        if post_count < 3:
            print(f"   Found {post_count} posts. Adding fresh test posts...")
            posts_to_create = [
                {"title": "Hello World", "status": ContentStatus.DRAFT},
                {"title": "Feature Announce", "status": ContentStatus.APPROVED},
                {"title": "Weekly Recap", "status": ContentStatus.SCHEDULED}
            ]
            
            for p_data in posts_to_create:
                post = Post(
                    project_id=project.id,
                    campaign_id=campaign.id,
                    title=p_data["title"],
                    content_text=f"This is a test post content for {p_data['title']}.",
                    status=p_data["status"],
                    platform="linkedin"
                )
                db.add(post)
            db.commit()
            print("   ✅ Added 3 test posts.")
        else:
            print(f"   ℹ️  Sufficient posts exist ({post_count}). Skipping creation.")

        print("\n✅ [SEED DEV] Completed successfully.")
        print(f"   Project ID: {project.id}")
        print(f"   Owner ID:   {target_user_id}")
        
    except Exception as e:
        print(f"\n❌ [SEED DEV] Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_dev_data()
