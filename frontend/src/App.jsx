import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Onboarding from './pages/Onboarding';
import Feed from './pages/Feed';
import Saved from './pages/Saved';
import Settings from './pages/Settings';
import CreateAgent from './pages/CreateAgent';  // NEW
import Learning from './pages/Learning';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/create-agent" element={<CreateAgent />} />  {/* NEW */}
        <Route path="/learning" element={<Learning />} />
      </Routes>
    </Router>
  );
}

export default App;