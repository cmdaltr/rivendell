import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login as apiLogin, loginAsGuest as apiLoginAsGuest } from '../api';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

const LoginPage = () => {
  const navigate = useNavigate();
  const { login: setUser } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiLogin(username, password);
      setUser(response.user);
      // Redirect to jobs page on success
      navigate('/jobs');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await apiLoginAsGuest();
      setUser(response.user);
      // Redirect to jobs page on success
      navigate('/jobs');
    } catch (err) {
      setError(err.response?.data?.detail || 'Guest login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="journey-detail">
      <section className="hero-section">
        <img
          src={heroImage}
          alt="Rivendell - The Last Homely House"
          className="hero-image"
          style={{
            transform: 'scale(0.2)',
            transformOrigin: 'center top'
          }}
        />
      </section>

      <header>
        <h2>Login</h2>
        <p>
          Access your Rivendell DF Acceleration Suite account.
        </p>
      </header>

      <div className="card">
        <h3>Sign In</h3>

        {error && (
          <div className="alert-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username or Email</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username or email"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              disabled={loading}
            />
          </div>

          <div style={{ marginTop: '0.5rem', marginBottom: '1rem' }}>
            <Link to="/forgot-password" className="text-link">
              Forgot password?
            </Link>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <button type="submit" disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
        </form>

        <div className="divider" data-text="or"></div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <button
            onClick={handleGuestLogin}
            disabled={loading}
            className="secondary"
            style={{ width: '100%' }}
          >
            {loading ? 'Continuing...' : 'Continue as Guest'}
          </button>
        </div>

        <div className="text-center" style={{ marginTop: '1.5rem' }}>
          Don't have an account?{' '}
          <Link to="/register" className="text-link">
            Register
          </Link>
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem', backgroundColor: 'rgba(240, 219, 165, 0.05)' }}>
        <h4 style={{ marginTop: 0 }}>Default Admin Account</h4>
        <p style={{ fontSize: '0.9rem', color: '#ccc' }}>
          <strong>Email:</strong> admin@rivendell.app<br />
          <strong>Password:</strong> IWasThere3000YearsAgo!
        </p>
        <p style={{ fontSize: '0.85rem', color: '#888', marginBottom: 0 }}>
          Please change this password after your first login in production environments.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
