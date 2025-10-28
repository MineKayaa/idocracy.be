#!/usr/bin/env python3
"""
Simple script to create an admin user directly in the database.
"""

import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add the app directory to the Python path
sys.path.append('/app')

from app.database import connect_to_mongo
from app.utils.auth import get_password_hash


async def create_admin_user():
    """Create an admin user directly in the database"""
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        
        from app.database import get_database
        db = get_database()
        
        # Check if admin user already exists
        existing_user = await db.users.find_one({"email": "admin@gov.tr"})
        
        if existing_user:
            print("✅ Admin user already exists!")
            print(f"   Email: {existing_user['email']}")
            print(f"   Name: {existing_user['name']}")
            print(f"   Roles: {existing_user['roles']}")
            print(f"   ID: {existing_user['_id']}")
            return
        
        # Create admin user document
        admin_user = {
            "_id": str(uuid.uuid4()),
            "email": "admin@gov.tr",
            "password_hash": get_password_hash("admin123"),
            "name": "System Administrator",
            "roles": ["admin"],
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.users.insert_one(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_user['email']}")
        print(f"   Name: {admin_user['name']}")
        print(f"   Roles: {admin_user['roles']}")
        print(f"   ID: {admin_user['_id']}")
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")
        print("   Default credentials: admin@gov.tr / admin123")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 Creating admin user for IDocracy API...")
    asyncio.run(create_admin_user()) 