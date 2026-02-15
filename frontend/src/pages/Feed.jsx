import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserFeed, getUserTopics, refreshTopicFeed, saveContent } from '../services/api';
import Navbar from '../components/Navbar';
import ContentCard from '../components/ContentCard';
import LoadingSpinner from '../components/LoadingSpinner';

function Feed() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [feed, setFeed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [savedItems, setSavedItems] = useState(new Set());

  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }
    loadTopicsAndFeed();
  }, [userId, navigate]);

  const loadTopicsAndFeed = async () => {
    try {
      // Load topics
      const topicsData = await getUserTopics(userId);
      
      // Filter only FEED topics (exclude learning)
      const feedTopics = (topicsData.topics || []).filter(t => t.topic_type !== 'learning');
      setTopics(feedTopics);
      
      // Auto-select first feed topic
      if (feedTopics.length > 0) {
        setSelectedTopic(feedTopics[0]);
      }
      
      // Load feed
      const feedData = await getUserFeed(userId);
      setFeed(feedData);
    } catch (err) {
      console.error('Failed to load:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchNow = async () => {
    if (!selectedTopic) return;
    
    setFetching(true);
    try {
      // NEW: Fetch only the selected topic
      await refreshTopicFeed(userId, selectedTopic.id);
      
      // Reload feed
      const feedData = await getUserFeed(userId);
      setFeed(feedData);
    } catch (err) {
      console.error('Failed to fetch:', err);
    } finally {
      setFetching(false);
    }
  };

  const handleSave = async (contentId) => {
    try {
      await saveContent(userId, contentId);
      setSavedItems(new Set([...savedItems, contentId]));
    } catch (err) {
      console.error('Failed to save:', err);
    }
  };

  // Get content for selected topic
  const getSelectedTopicContent = () => {
    if (!feed || !selectedTopic) return [];
    const topicFeed = feed.topics.find(t => t.topic_id === selectedTopic.id);
    return topicFeed?.items || [];
  };

  if (loading) {
    return (
      <div>
        <Navbar />
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="flex h-[calc(100vh-64px)]">
        {/* Left Sidebar - Topics List */}
        <div className="w-64 bg-white border-r overflow-y-auto">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-800">Feed Topics</h2>
          </div>
          
          {topics.length === 0 ? (
            <div className="p-4 text-gray-500 text-sm">
              No topics yet. Create one in the Create Agent tab.
            </div>
          ) : (
            <div className="py-2">
              {topics.map((topic) => (
                <button
                  key={topic.id}
                  onClick={() => setSelectedTopic(topic)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${
                    selectedTopic?.id === topic.id
                      ? 'bg-blue-50 border-l-4 border-blue-600'
                      : ''
                  }`}
                >
                  <div className="font-medium text-gray-900">
                    {topic.topic_name}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {topic.description?.substring(0, 50)}...
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            {!selectedTopic ? (
              <div className="text-center py-12">
                <p className="text-gray-600 text-lg">Select a topic to view content</p>
              </div>
            ) : (
              <>
                {/* Topic Header with Fetch Button */}
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                      {selectedTopic.topic_name}
                    </h1>
                    <p className="text-gray-600 mt-1">
                      {selectedTopic.description}
                    </p>
                  </div>
                  
                  <button
                    onClick={handleFetchNow}
                    disabled={fetching}
                    className="btn-primary"
                  >
                    {fetching ? 'Fetching...' : '🔄 Fetch Now'}
                  </button>
                </div>

                {/* Content Grid */}
                {getSelectedTopicContent().length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-600">No content yet. Click "Fetch Now" to get fresh content!</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {getSelectedTopicContent().map((item) => (
                      <ContentCard
                        key={item.id}
                        content={item}
                        onSave={handleSave}
                        isSaved={savedItems.has(item.id)}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Feed;