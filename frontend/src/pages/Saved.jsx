import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSavedContent, unsaveContent } from '../services/api';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';

function Saved() {
  const navigate = useNavigate();
  const [saved, setSaved] = useState([]);
  const [loading, setLoading] = useState(true);

  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }
    loadSaved();
  }, [userId, navigate]);

  const loadSaved = async () => {
    try {
      const data = await getSavedContent(userId);
      setSaved(data.items);
    } catch (err) {
      console.error('Failed to load saved content:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUnsave = async (savedId) => {
    try {
      await unsaveContent(savedId);
      setSaved(saved.filter(item => item.id !== savedId));
    } catch (err) {
      console.error('Failed to unsave content:', err);
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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Saved Content</h1>

        {saved.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No saved content yet</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {saved.map((item) => (
              <div key={item.id} className="card">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {item.content.title}
                  </h3>
                  <button
                    onClick={() => handleUnsave(item.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ✕
                  </button>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">
                  {item.content.summary}
                </p>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {item.content.source}
                  </span>
                  
                    < a href={item.content.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                  >
                    Read more →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Saved;