import React, { useState } from 'react';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement login logic
    console.log('Login attempt:', username);
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
        <h3>Coming Soon</h3>
        <p>
          Authentication and user management features are currently under development.
        </p>

        <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              disabled
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
              disabled
            />
          </div>

          <button type="submit" disabled style={{ marginTop: '1rem' }}>
            Login (Disabled)
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
