import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUser } from '../services/api';
import Navbar from '../components/Navbar';
import LoadingSpinner from '../components/LoadingSpinner';

function Settings() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/');
      return;
    }
    loadUser();
  }, [userId, navigate]);

  const loadUser = async () => {
    try {
      const userData = await getUser(userId);
      setUser(userData);
    } catch (err) {
      console.error('Failed to load user:', err);
    } finally {
      setLoading(false);
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
      
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Personal Details
            </h2>
            <button className="text-blue-600 hover:text-blue-700 text-sm">
              ✏️ Edit
            </button>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 py-3 border-b">
              <div className="font-medium text-gray-600">Email</div>
              <div className="col-span-2 text-gray-900">{user?.email || 'N/A'}</div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 py-3 border-b">
              <div className="font-medium text-gray-600">Mobile Number</div>
              <div className="col-span-2 text-gray-900">{user?.mobile_number || 'Not set'}</div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 py-3 border-b">
              <div className="font-medium text-gray-600">Username</div>
              <div className="col-span-2 text-gray-900">{user?.username || 'N/A'}</div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 py-3 border-b">
              <div className="font-medium text-gray-600">Password</div>
              <div className="col-span-2 text-gray-900">••••••••</div>
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-500 mt-4 text-center">
          As of now, no authentication or verification is required. Just unique username.
        </p>
      </div>
    </div>
  );
}

export default Settings;