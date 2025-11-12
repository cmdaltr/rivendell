import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import NewAnalysis from './components/NewAnalysis';
import JobList from './components/JobList';
import JobDetails from './components/JobDetails';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>🧙‍♂️ Elrond Web Interface</h1>
          <nav>
            <Link to="/">New Analysis</Link>
            <Link to="/jobs">Jobs</Link>
          </nav>
        </header>

        <main className="App-main">
          <Routes>
            <Route path="/" element={<NewAnalysis />} />
            <Route path="/jobs" element={<JobList />} />
            <Route path="/jobs/:jobId" element={<JobDetails />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <p>
            Elrond v2.1.0 - Digital Forensics Analysis Platform
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
