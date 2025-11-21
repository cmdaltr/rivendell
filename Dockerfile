# Rivendell DF Acceleration Suite Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    gcc \
    g++ \
    make \
    git \
    cmake \
    # Forensic tools
    sleuthkit \
    libewf-dev \
    afflib-tools \
    ewf-tools \
    # Utilities
    curl \
    wget \
    unzip \
    p7zip-full \
    # SSH for remote acquisition
    openssh-client \
    # Additional tools
    exiftool \
    yara \
    clamav \
    clamav-daemon \
    # Network tools
    netcat-openbsd \
    # APFS-fuse dependencies
    libbz2-dev \
    libattr1-dev \
    libfuse-dev \
    fuse3 \
    # Volatility dependencies
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install apfs-fuse for macOS image support
RUN cd /tmp && \
    git clone https://github.com/sgan81/apfs-fuse.git && \
    cd apfs-fuse && \
    git submodule init && \
    git submodule update && \
    mkdir build && cd build && \
    cmake .. && \
    make && \
    make install && \
    cd / && rm -rf /tmp/apfs-fuse

# Install Volatility3
RUN cd /opt && \
    git clone https://github.com/volatilityfoundation/volatility3.git && \
    cd volatility3 && \
    pip install -r requirements.txt && \
    python3 setup.py install && \
    # Download Windows symbol tables
    mkdir -p volatility3/symbols/windows && \
    cd /tmp && \
    git clone https://github.com/JPCERTCC/Windows-Symbol-Tables.git && \
    cp -r Windows-Symbol-Tables/symbols/windows/*.json /opt/volatility3/volatility3/symbols/windows/ 2>/dev/null || true && \
    rm -rf /tmp/Windows-Symbol-Tables && \
    # Make volatility3 accessible
    ln -s /opt/volatility3/vol.py /usr/local/bin/vol3 && \
    chmod +x /usr/local/bin/vol3

# Create rivendell user
RUN useradd -m -s /bin/bash rivendell && \
    mkdir -p /app /data /evidence /output /data/mordor && \
    chown -R rivendell:rivendell /app /data /evidence /output

# Clone Mordor Security Datasets
RUN git clone https://github.com/OTRF/Security-Datasets.git /data/mordor && \
    chown -R rivendell:rivendell /data/mordor

WORKDIR /app

# Copy requirements first for better caching
COPY --chown=rivendell:rivendell requirements/ ./requirements/
COPY --chown=rivendell:rivendell pyproject.toml .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements/base.txt && \
    pip install -r requirements/web.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -r requirements/dev.txt

USER rivendell

# Copy application code
COPY --chown=rivendell:rivendell . .

# Expose ports
EXPOSE 8000

# Development command
CMD ["python3", "-m", "uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

USER rivendell

# Copy only necessary application code
COPY --chown=rivendell:rivendell acquisition/ ./acquisition/
COPY --chown=rivendell:rivendell analysis/ ./analysis/
COPY --chown=rivendell:rivendell web/ ./web/
COPY --chown=rivendell:rivendell cli/ ./cli/
COPY --chown=rivendell:rivendell config/ ./config/

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "web" ]; then\n\
    exec python3 -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000\n\
elif [ "$1" = "acquire" ]; then\n\
    shift\n\
    exec python3 acquisition/python/gandalf.py "$@"\n\
elif [ "$1" = "analyze" ]; then\n\
    shift\n\
    exec python3 analysis/elrond.py "$@"\n\
else\n\
    exec python3 cli/rivendell.py "$@"\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["web"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
