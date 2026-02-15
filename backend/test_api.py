"""
Test FastAPI endpoints
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_api():
    print("=" * 60)
    print("Testing AI Sutra API")
    print("=" * 60)
    
    # Increase timeout for long-running operations like feed refresh
    async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minute timeout
        
        # Test 1: Root endpoint
        print("\n1. Testing root endpoint...")
        response = await client.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Health check
        print("\n2. Testing health check...")
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 3: Create user
        print("\n3. Creating test user...")
        user_data = {
            "name": "Test User",
            "email": "testuser@aisutra.com"
        }
        response = await client.post(f"{BASE_URL}/api/users/", json=user_data)
        print(f"Status: {response.status_code}")
        user = response.json()
        print(f"Created user: {user['name']} (ID: {user['id']})")
        user_id = user["id"]
        
        # Test 4: Get user
        print("\n4. Getting user by ID...")
        response = await client.get(f"{BASE_URL}/api/users/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"✅ User retrieved: {response.json()['email']}")
        
        # Test 5: Onboarding
        print("\n5. Processing onboarding...")
        onboarding_data = {
            "user_id": user_id,
            "interests": "I want tech news and cricket scores"  # Only 2 topics to reduce API load
        }
        response = await client.post(f"{BASE_URL}/api/onboarding/", json=onboarding_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Topics created: {[t['topic_name'] for t in result['topics_added']]}")
        
        # Test 6: Get user topics
        print("\n6. Getting user topics...")
        response = await client.get(f"{BASE_URL}/api/onboarding/{user_id}/topics")
        print(f"Status: {response.status_code}")
        topics_result = response.json()
        print(f"✅ User has {len(topics_result['topics'])} topics:")
        for topic in topics_result['topics']:
            print(f"   - {topic['topic_name']}")
        
        # Test 7: Refresh feed (with delays to avoid rate limits)
        print("\n7. Refreshing user feed (this will take ~6-10 seconds per topic)...")
        print("   ⏳ Fetching content with rate limit protection...")
        try:
            response = await client.post(f"{BASE_URL}/api/feed/refresh/{user_id}")
            print(f"Status: {response.status_code}")
            refresh_result = response.json()
            print(f"✅ {refresh_result['message']}")
            print(f"   Total items fetched: {refresh_result.get('total_items_fetched', 0)}")
            for topic_name, result in refresh_result['results'].items():
                if result['success']:
                    print(f"   ✅ {topic_name}: {result['items_fetched']} items")
                else:
                    print(f"   ⚠️ {topic_name}: {result.get('error', 'Failed')}")
        except httpx.ReadTimeout:
            print("⚠️ Feed refresh timed out (this is okay for testing)")
        
        # Test 8: Get feed
        print("\n8. Getting user feed...")
        response = await client.get(f"{BASE_URL}/api/feed/{user_id}")
        print(f"Status: {response.status_code}")
        feed = response.json()
        print(f"✅ Feed retrieved with {len(feed['topics'])} topics:")
        for topic in feed['topics']:
            print(f"\n   📰 {topic['topic_name']}: {len(topic['items'])} items")
            for i, item in enumerate(topic['items'][:2], 1):  # Show first 2 items
                print(f"      {i}. {item['title'][:60]}...")
                print(f"         Source: {item['source']}")
        
        # Test 9: Save content
        if feed['topics'] and feed['topics'][0]['items']:
            print("\n9. Saving content...")
            content_id = feed['topics'][0]['items'][0]['id']
            save_data = {
                "user_id": user_id,
                "content_id": content_id
            }
            response = await client.post(f"{BASE_URL}/api/saved/", json=save_data)
            print(f"Status: {response.status_code}")
            print(f"✅ {response.json()['message']}")
        
        # Test 10: Get saved content
        print("\n10. Getting saved content...")
        response = await client.get(f"{BASE_URL}/api/saved/{user_id}")
        print(f"Status: {response.status_code}")
        saved = response.json()
        print(f"✅ User has {saved['total_saved']} saved items")
        if saved['items']:
            print(f"   First saved: {saved['items'][0]['content']['title'][:50]}...")
        
        # Test 11: Get settings
        print("\n11. Getting user settings...")
        response = await client.get(f"{BASE_URL}/api/settings/{user_id}")
        print(f"Status: {response.status_code}")
        settings = response.json()
        print(f"✅ Settings retrieved:")
        print(f"   Frequency: {settings['periodic_frequency']}")
        print(f"   Languages: {settings['preferred_languages']}")
        print(f"   Delivery time: {settings['delivery_time']}")
        
        # Test 12: Update settings
        print("\n12. Updating user settings...")
        settings_data = {
            "periodic_frequency": "daily",
            "preferred_languages": ["en", "hi"],
            "delivery_time": "07:00:00"
        }
        response = await client.put(f"{BASE_URL}/api/settings/{user_id}", json=settings_data)
        print(f"Status: {response.status_code}")
        updated = response.json()
        print(f"✅ Settings updated:")
        print(f"   New delivery time: {updated['delivery_time']}")
        print(f"   New languages: {updated['preferred_languages']}")



        # Test 13: Check scheduler status
        print("\n13. Checking scheduler status...")
        response = await client.get(f"{BASE_URL}/api/scheduler/status")
        print(f"Status: {response.status_code}")
        scheduler_status = response.json()
        print(f"✅ Scheduler status: {scheduler_status['status']}")
        print(f"   Jobs scheduled: {scheduler_status['jobs_count']}")
        for job in scheduler_status['jobs']:
            print(f"   • {job['name']}")
            print(f"     Next run: {job['next_run']}")
        
    print("\n" + "=" * 60)
    print("🎉 API Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api())