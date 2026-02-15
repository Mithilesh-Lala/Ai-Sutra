"""
Test Claude API client
"""

import asyncio
from app.utils.claude_client import get_claude_client

async def main():
    print("=" * 60)
    print("Testing Claude API Client")
    print("=" * 60)
    
    # Get client
    print("\n1. Initializing Claude client...")
    try:
        client = get_claude_client()
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test connection
    print("\n2. Testing API connection...")
    connected = await client.test_connection()
    if connected:
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        return
    
    # Test interest parsing
    print("\n3. Testing interest parsing...")
    interests = "I want tech news, cricket scores, and daily Bible verses"
    print(f"   Input: '{interests}'")
    
    topics = await client.parse_interests(interests)
    print(f"✅ Parsed {len(topics)} topics:")
    for topic in topics:
        print(f"   - {topic['name']}: {topic['description']}")
    
    # Test content fetching
    print("\n4. Testing content fetching...")
    if topics:
        test_topic = topics[0]
        print(f"   Fetching content for: {test_topic['name']}")
        
        content = await client.fetch_content_for_topic(
            topic_name=test_topic['name'],
            topic_description=test_topic['description'],
            max_items=3
        )
        
        print(f"✅ Fetched {len(content)} content items:")
        for i, item in enumerate(content, 1):
            print(f"\n   Item {i}:")
            print(f"   Title: {item.get('title', 'N/A')}")
            print(f"   Source: {item.get('source', 'N/A')}")
            print(f"   URL: {item.get('url', 'N/A')[:50]}...")
    
    print("\n" + "=" * 60)
    print("Claude API Client Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())