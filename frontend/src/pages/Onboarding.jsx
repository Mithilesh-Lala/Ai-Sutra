import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createUser, processOnboarding } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [interests, setInterests] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUserCreate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await createUser({ name, email });
      localStorage.setItem('userId', user.id);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleInterestsSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const userId = localStorage.getItem('userId');
      await processOnboarding(userId, interests);
      navigate('/feed');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process interests');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            {step === 1 ? 'Create Your Account' : 'Tell Us Your Interests'}
          </h1>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleUserCreate}>
              <div className="mb-4">
                <label className="block text-gray-700 font-medium mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-field"
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <button
                type="submit"
                className="btn-primary w-full"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Continue'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleInterestsSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  What interests you?
                </label>
                <textarea
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                  className="input-field min-h-32"
                  placeholder="E.g., I want tech news, cricket scores, and daily motivation"
                  required
                />
                <p className="text-sm text-gray-500 mt-2">
                  Just describe what you want in natural language
                </p>
              </div>

              {loading ? (
                <LoadingSpinner />
              ) : (
                <button type="submit" className="btn-primary w-full">
                  Create My Feed
                </button>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default Onboarding;