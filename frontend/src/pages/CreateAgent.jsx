import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';
import { getUserTopics, processOnboarding, deleteTopic, updateTopic } from '../services/api';

function CreateAgent() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('feed');  // 'feed' or 'learning'
  const [editingTopic, setEditingTopic] = useState(null);  // track which topic is being edited
  
  // Form state
  const [topicName, setTopicName] = useState('');
  const [details, setDetails] = useState('');
  const [language, setLanguage] = useState('');
  const [schedule, setSchedule] = useState('daily');
  const [scheduleTime, setScheduleTime] = useState('08:00');
  const [feedSource, setFeedSource] = useState('internet');
  const [learningPeriod, setLearningPeriod] = useState('');
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }
    loadTopics();
  }, [userId, navigate]);

  const loadTopics = async () => {
    try {
      const data = await getUserTopics(userId);
      setTopics(data.topics || []);
    } catch (err) {
      console.error('Failed to load topics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      if (editingTopic) {
        // UPDATE existing topic
        await updateTopic(editingTopic.id, {
          topic_name: topicName,
          description: details,
          feed_source: modalType === 'learning' ? 'ai' : feedSource,
          learning_period_days: modalType === 'learning' ? parseInt(learningPeriod) : null
        });
      } else {
        // CREATE new topic
        let interestText;
        
        if (modalType === 'learning') {
          interestText = `${topicName}. ${details}. Language: ${language || 'English'}. Schedule: ${schedule} at ${scheduleTime}. Topic Type: learning. Learning Period: ${learningPeriod} days`;
        } else {
          interestText = `${topicName}. ${details}. Language: ${language || 'English'}. Schedule: ${schedule} at ${scheduleTime}. Topic Type: feed. Feed Source: ${feedSource}`;
        }
        
        await processOnboarding(userId, interestText);
      }
      
      // Reload topics
      await loadTopics();
      
      // Close modal and reset form
      setShowModal(false);
      setEditingTopic(null);
      resetForm();
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${editingTopic ? 'update' : 'create'} agent`);
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setTopicName('');
    setDetails('');
    setLanguage('');
    setSchedule('daily');
    setScheduleTime('08:00');
    setFeedSource('internet');
    setLearningPeriod('');
  };

  const handleEditTopic = (topic) => {
    // Populate form with existing topic data
    setTopicName(topic.topic_name);
    setDetails(topic.description || '');
    setLanguage('');
    setSchedule('daily');
    setScheduleTime('08:00');
    setFeedSource(topic.feed_source || 'internet');
    setLearningPeriod(topic.learning_period_days?.toString() || '');
    setModalType(topic.topic_type || 'feed');
    setEditingTopic(topic);
    setShowModal(true);
  };

  const handleDeleteTopic = async (topicId, topicName) => {
    if (!confirm(`Delete "${topicName}"? This will remove all associated content.`)) {
      return;
    }

    try {
      await deleteTopic(topicId);
      await loadTopics();
    } catch (err) {
      alert('Failed to delete topic: ' + (err.response?.data?.detail || 'Unknown error'));
    }
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
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Agent</h1>
          
          <div className="flex gap-3">
            <button
              onClick={() => {
                setModalType('feed');
                setEditingTopic(null);
                resetForm();
                setShowModal(true);
              }}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-md"
            >
              + Feed Agent
            </button>
            
            <button
              onClick={() => {
                setModalType('learning');
                setEditingTopic(null);
                resetForm();
                setShowModal(true);
              }}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors shadow-md"
            >
              + Learning Agent
            </button>
          </div>
        </div>

        {topics.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No agents yet. Create your first one!</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topics.map((topic) => (
              <div key={topic.id} className="card">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {topic.topic_name}
                  </h3>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => handleEditTopic(topic)}
                      className="text-blue-600 hover:text-blue-700 text-xl"
                    >
                      ✏️
                    </button>
                    <button 
                      onClick={() => handleDeleteTopic(topic.id, topic.topic_name)}
                      className="text-red-600 hover:text-red-700 text-xl"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                
                <p className="text-gray-600 text-sm mb-2">
                  {topic.description}
                </p>
                
                <div className="text-xs text-gray-500">
                  Created: {new Date(topic.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Agent Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 max-h-screen overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingTopic 
                ? `Edit ${modalType === 'learning' ? 'Learning' : 'Feed'} Agent`
                : `Create ${modalType === 'learning' ? 'Learning' : 'Feed'} Agent`
              }
            </h2>
            
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
                {error}
              </div>
            )}
            
            <form onSubmit={handleCreateAgent}>
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Topic Name *
                </label>
                <input
                  type="text"
                  value={topicName}
                  onChange={(e) => setTopicName(e.target.value)}
                  className="input-field"
                  placeholder={modalType === 'learning' ? "e.g., Python for Data Engineering" : "e.g., Cricket News"}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Some Details
                </label>
                <textarea
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                  className="input-field"
                  placeholder={modalType === 'learning' ? "e.g., I want to become a data engineer" : "e.g., Indian Mens Cricket news"}
                  rows="3"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Language
                </label>
                <input
                  type="text"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="input-field"
                  placeholder="e.g., English, Hindi, Spanish, French"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Schedule
                </label>
                <select
                  value={schedule}
                  onChange={(e) => setSchedule(e.target.value)}
                  className="input-field"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Schedule Time
                </label>
                <input
                  type="time"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  className="input-field"
                />
              </div>
              
              {/* Learning Period - ONLY for Learning Agents */}
              {modalType === 'learning' && (
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    Learning Period (in days) *
                  </label>
                  <input
                    type="number"
                    value={learningPeriod}
                    onChange={(e) => setLearningPeriod(e.target.value)}
                    className="input-field"
                    placeholder="e.g., 30"
                    min="1"
                    required
                  />
                </div>
              )}
              
              {/* Feed Source - ONLY for Feed Agents */}
              {modalType === 'feed' && (
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <label className="block text-gray-700 font-medium">
                      Feed Source *
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowInfoModal(true)}
                      className="text-blue-600 hover:text-blue-700 text-lg"
                      title="Learn about feed sources"
                    >
                      ℹ️
                    </button>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="feedSource"
                        value="internet"
                        checked={feedSource === 'internet'}
                        onChange={(e) => setFeedSource(e.target.value)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium">📰 From Internet</div>
                        <div className="text-xs text-gray-500">Fetch real articles and news</div>
                      </div>
                    </label>
                    
                    <label className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="feedSource"
                        value="ai"
                        checked={feedSource === 'ai'}
                        onChange={(e) => setFeedSource(e.target.value)}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium">🤖 From AI</div>
                        <div className="text-xs text-gray-500">AI-generated analysis and insights</div>
                      </div>
                    </label>
                  </div>
                </div>
              )}
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="btn-primary flex-1"
                  disabled={creating}
                >
                  {creating 
                    ? (editingTopic ? 'Updating...' : 'Creating...') 
                    : (editingTopic ? 'Update Agent' : 'Create Agent')
                  }
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingTopic(null);
                    resetForm();
                  }}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Info Modal */}
      {showInfoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">Feed Source Options</h2>
            
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">📰</span>
                  <h3 className="font-semibold text-gray-900">From Internet</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">
                  Fetches real articles and content from websites with URLs.
                </p>
                <p className="text-xs text-gray-600">
                  <strong>Best for:</strong> News, Sports, Politics, Trending Topics, Jokes, Memes
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">🤖</span>
                  <h3 className="font-semibold text-gray-900">From AI</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">
                  Claude AI generates unified, comprehensive responses using latest data.
                </p>
                <p className="text-xs text-gray-600">
                  <strong>Best for:</strong> Astrology, Personalized Advice, Market Analysis, Educational Content
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setShowInfoModal(false)}
              className="btn-primary w-full mt-6"
            >
              Got it!
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CreateAgent;