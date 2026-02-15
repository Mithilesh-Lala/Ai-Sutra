"""
Test Pydantic schemas
"""
from datetime import datetime, time
from app.schemas import (
    UserCreate, UserResponse,
    InterestInput, OnboardingRequest,
    TopicCreate, TopicResponse,
    ContentCreate, ContentResponse,
    SaveContentRequest,
    UserSettingsUpdate,
    FeedResponse, TopicFeed
)

print("=" * 60)
print("Testing AI Sutra Pydantic Schemas")
print("=" * 60)

# Test 1: User Creation
print("\n1. Testing UserCreate schema...")
try:
    user_data = UserCreate(name="Mit", email="mit@example.com")
    print(f"✅ UserCreate: {user_data.model_dump()}")
except Exception as e:
    print(f"❌ UserCreate failed: {e}")

# Test 2: Invalid Email
print("\n2. Testing invalid email validation...")
try:
    invalid_user = UserCreate(name="Test", email="not-an-email")
    print(f"❌ Should have failed but got: {invalid_user}")
except Exception as e:
    print(f"✅ Correctly rejected invalid email: {type(e).__name__}")

# Test 3: Interest Input
print("\n3. Testing InterestInput schema...")
try:
    interest = InterestInput(interest_text="I want tech news, cricket scores, and daily Bible verses")
    print(f"✅ InterestInput: {interest.interest_text[:50]}...")
except Exception as e:
    print(f"❌ InterestInput failed: {e}")

# Test 4: Interest too short
print("\n4. Testing interest text length validation...")
try:
    short_interest = InterestInput(interest_text="short")
    print(f"❌ Should have failed but got: {short_interest}")
except Exception as e:
    print(f"✅ Correctly rejected short text: {type(e).__name__}")

# Test 5: Onboarding Request
print("\n5. Testing OnboardingRequest schema...")
try:
    onboarding = OnboardingRequest(
        user_id=1,
        interests="I want tech news, cricket scores, and daily motivation"
    )
    print(f"✅ OnboardingRequest: user_id={onboarding.user_id}, interests={onboarding.interests[:40]}...")
except Exception as e:
    print(f"❌ OnboardingRequest failed: {e}")

# Test 6: Topic Creation
print("\n6. Testing TopicCreate schema...")
try:
    topic = TopicCreate(
        topic_name="Tech News",
        description="Latest technology news and updates",
        agent_config={"sources": ["techcrunch", "verge"], "frequency": "daily"}
    )
    print(f"✅ TopicCreate: {topic.topic_name}")
    print(f"   Agent config: {topic.agent_config}")
except Exception as e:
    print(f"❌ TopicCreate failed: {e}")

# Test 7: Content Creation
print("\n7. Testing ContentCreate schema...")
try:
    content = ContentCreate(
        topic_id=1,
        title="Claude 4 Released",
        summary="Anthropic launches new Claude 4 model",
        content="Full article content here...",
        url="https://example.com/claude4",
        image_url="https://example.com/image.jpg",
        source="TechCrunch"
    )
    print(f"✅ ContentCreate: {content.title}")
    print(f"   URL: {content.url}")
except Exception as e:
    print(f"❌ ContentCreate failed: {e}")

# Test 8: Save Content Request
print("\n8. Testing SaveContentRequest schema...")
try:
    save_request = SaveContentRequest(user_id=1, content_id=5)
    print(f"✅ SaveContentRequest: user={save_request.user_id}, content={save_request.content_id}")
except Exception as e:
    print(f"❌ SaveContentRequest failed: {e}")

# Test 9: User Settings
print("\n9. Testing UserSettingsUpdate schema...")
try:
    settings = UserSettingsUpdate(
        periodic_frequency="daily",
        preferred_languages=["en", "hi"],
        delivery_time=time(7, 30)
    )
    print(f"✅ UserSettingsUpdate: frequency={settings.periodic_frequency}")
    print(f"   Languages: {settings.preferred_languages}")
    print(f"   Delivery time: {settings.delivery_time}")
except Exception as e:
    print(f"❌ UserSettingsUpdate failed: {e}")

# Test 10: Invalid frequency
print("\n10. Testing invalid frequency validation...")
try:
    bad_settings = UserSettingsUpdate(
        periodic_frequency="hourly",  # Not allowed
        preferred_languages=["en"]
    )
    print(f"❌ Should have failed but got: {bad_settings}")
except Exception as e:
    print(f"✅ Correctly rejected invalid frequency: {type(e).__name__}")

# Test 11: TopicFeed (nested schema)
print("\n11. Testing TopicFeed (nested) schema...")
try:
    content1 = ContentResponse(
        id=1,
        topic_id=1,
        title="Article 1",
        summary="Summary 1",
        content="Content 1",
        url="https://example.com/1",
        image_url=None,
        source="Source 1",
        fetched_at=datetime.now()
    )
    
    content2 = ContentResponse(
        id=2,
        topic_id=1,
        title="Article 2",
        summary="Summary 2",
        content="Content 2",
        url="https://example.com/2",
        image_url=None,
        source="Source 2",
        fetched_at=datetime.now()
    )
    
    topic_feed = TopicFeed(
        topic_name="Tech News",
        topic_id=1,
        items=[content1, content2]
    )
    print(f"✅ TopicFeed: {topic_feed.topic_name} with {len(topic_feed.items)} items")
except Exception as e:
    print(f"❌ TopicFeed failed: {e}")

# Test 12: FeedResponse (complex nested schema)
print("\n12. Testing FeedResponse (complex nested) schema...")
try:
    feed = FeedResponse(
        user_id=1,
        date=datetime.now(),
        topics=[topic_feed]
    )
    print(f"✅ FeedResponse: user={feed.user_id}, topics={len(feed.topics)}")
except Exception as e:
    print(f"❌ FeedResponse failed: {e}")

# Test 13: JSON Serialization
print("\n13. Testing JSON serialization...")
try:
    user = UserCreate(name="Test User", email="test@example.com")
    json_data = user.model_dump_json()
    print(f"✅ JSON serialization works")
    print(f"   {json_data}")
except Exception as e:
    print(f"❌ JSON serialization failed: {e}")

# Test 14: JSON Deserialization
print("\n14. Testing JSON deserialization...")
try:
    json_string = '{"name": "JSON User", "email": "json@example.com"}'
    user_from_json = UserCreate.model_validate_json(json_string)
    print(f"✅ JSON deserialization works: {user_from_json.name}")
except Exception as e:
    print(f"❌ JSON deserialization failed: {e}")

print("\n" + "=" * 60)
print("Schema Testing Complete!")
print("=" * 60)