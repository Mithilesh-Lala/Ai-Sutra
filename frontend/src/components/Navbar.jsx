import { Link, useLocation, useNavigate } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const isActive = (path) => location.pathname === path;
  
  const handleLogoClick = (e) => {
    e.preventDefault();
    const userId = localStorage.getItem('userId');
    if (userId) {
      navigate('/feed');  // Logged in → Go to feed
    } else {
      navigate('/');  // Not logged in → Go to login
    }
  };
  
  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <a href="#" onClick={handleLogoClick} className="flex items-center space-x-2 cursor-pointer">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg"></div>
            <span className="text-xl font-bold text-gray-900">AI Sutra</span>
          </a>
          
          <div className="flex space-x-4">
            <Link
              to="/feed"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/feed')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Feed
            </Link>
            
            <Link
              to="/learning"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/learning')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Learning
            </Link>
            
            <Link
              to="/create-agent"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/create-agent')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Create Agent
            </Link>
            
            <Link
              to="/settings"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/settings')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Settings
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;