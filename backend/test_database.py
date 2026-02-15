"""
Test database setup
"""
import sys
import traceback

try:
    print("Importing database modules...")
    from app.database import init_db, engine, Base
    print("✅ Database module imported")
    
    print("Importing models...")
    from app.models import User, Topic, ContentPool
    print("✅ Models imported")
    
    from sqlalchemy import inspect
    
    print("\nCreating database tables...")
    init_db()
    
    print("\nVerifying tables created:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "users",
        "user_interests", 
        "topics",
        "user_topics",
        "content_pool",
        "saved_content",
        "user_settings"
    ]
    
    for table in expected_tables:
        if table in tables:
            print(f"✅ {table}")
        else:
            print(f"❌ {table} - NOT FOUND")
    
    print(f"\n📊 Total tables created: {len(tables)}")
    print("\n🎉 Database setup complete!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)