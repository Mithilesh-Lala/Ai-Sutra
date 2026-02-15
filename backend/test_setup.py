"""Test to verify all dependencies are working"""

import sys
print(f"Python version: {sys.version}")

# Test imports
try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import anthropic
    print(f"✅ Anthropic {anthropic.__version__}")
except ImportError as e:
    print(f"❌ Anthropic: {e}")

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy: {e}")

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("✅ APScheduler")
except ImportError as e:
    print(f"❌ APScheduler: {e}")

print("\n🎉 All dependencies installed successfully!")