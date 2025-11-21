import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import GandalfLanding from './components/GandalfLanding';
import ElrondLanding from './components/ElrondLanding';
import MordorLanding from './components/MordorLanding';
import LoginPage from './components/LoginPage';
import HelpPage from './components/HelpPage';
import JobList from './components/JobList';
import JobDetails from './components/JobDetails';
import Archive from './components/Archive';
import './App.css';

function App() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const mapBackground = `${process.env.PUBLIC_URL}/images/middle_earth.png`;

  return (
    <Router>
      <div
        className="App"
        style={{
          backgroundImage: `url(${mapBackground})`,
          backgroundSize: 'cover',
          backgroundAttachment: 'fixed',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: 'rgba(15, 15, 35, 0.72)',
          backgroundBlendMode: 'multiply',
        }}
      >
        <header className="App-header">
          <nav>
            <div className="nav-left">
              <Link to="/">Home</Link>
              <Link to="/gandalf">Gandalf</Link>
              <Link to="/elrond">Elrond</Link>
              <Link to="/mordor">Mordor</Link>
            </div>
            <div className="nav-right">
              <Link to="/login">Login</Link>
              <Link to="/jobs">Jobs</Link>
              <Link to="/help">Help</Link>
              <a href="https://github.com/cmdaltr" target="_blank" rel="noopener noreferrer">@cmdaltr</a>
            </div>
          </nav>
        </header>

        <main className="App-main">
          <Routes>
            <Route path="/" element={<Home onScrollProgress={setScrollProgress} />} />
            <Route path="/gandalf" element={<GandalfLanding />} />
            <Route path="/elrond" element={<ElrondLanding />} />
            <Route path="/mordor" element={<MordorLanding />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/help" element={<HelpPage />} />
            <Route path="/jobs" element={<JobList />} />
            <Route path="/jobs/:jobId" element={<JobDetails />} />
            <Route path="/archive" element={<Archive />} />
          </Routes>
        </main>

        <footer className="App-footer">
          <p>
            Rivendell v1.0.0 - Digital Forensics Acceleration Suite
          </p>
          <p className="attribution">
            This project contains references to "The Lord of the Rings" by J.R.R. Tolkien.<br />
            All trademarks and copyrights for that work belong to their respective owners.<br />
            This code is not affiliated with or endorsed by the Tolkien Estate or Peter Jackson.
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
