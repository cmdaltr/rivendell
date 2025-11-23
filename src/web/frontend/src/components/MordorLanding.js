import React from 'react';

const heroImage = `${process.env.PUBLIC_URL}/images/rivendell.png`;

const MordorLanding = () => {
  return (
    <div className="journey-detail">
      <section className="hero-section">
        <img
          src={heroImage}
          alt="Mordor Recordings"
          className="hero-image"
          style={{
            transform: 'scale(0.2)',
            transformOrigin: 'center top'
          }}
        />
      </section>

      <header>
        <h2>Mordor Recordings</h2>
        <p>
          Access pre-recorded security event datasets from the OTRF Mordor project for threat research, detection development, and testing.
        </p>
      </header>

      <div className="card">
        <h3>Coming Soon</h3>
        <p>
          This feature will provide integrated access to the Mordor Security Datasets repository,
          allowing you to browse and import pre-recorded security events directly into Rivendell for analysis.
        </p>
        <p>
          In the meantime, you can access the datasets directly at:{' '}
          <a
            href="https://github.com/OTRF/Security-Datasets"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#a7db6c' }}
          >
            https://github.com/OTRF/Security-Datasets
          </a>
        </p>
      </div>
    </div>
  );
};

export default MordorLanding;
