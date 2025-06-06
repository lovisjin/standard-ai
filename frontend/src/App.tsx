import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Summarizer from "./components/Summarizer";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link 
                  to="/" 
                  className="inline-flex items-center px-1 pt-1 text-gray-900"
                >
                  피드백 통계
                </Link>
                <Link 
                  to="/summarize" 
                  className="inline-flex items-center px-1 pt-1 text-gray-900"
                >
                  텍스트 요약
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/summarize" element={<Summarizer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
