# FixGoblin - Multi-Language Autonomous Debugging System
# Docker Image with Python, C++, Java, JavaScript, and Go support

FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies and language runtimes
RUN apt-get update && apt-get install -y \
    # Python
    python3.10 \
    python3-pip \
    python3-venv \
    # C/C++ compilers
    gcc \
    g++ \
    make \
    # Java
    default-jdk \
    default-jre \
    # Node.js/JavaScript
    nodejs \
    npm \
    # Go
    golang-go \
    # Utilities
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
RUN pip3 install --upgrade pip setuptools wheel

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set environment variables for FixGoblin
ENV FIXGOBLIN_TIMEOUT=10
ENV FIXGOBLIN_MEMORY_LIMIT=512

# Expose port for Streamlit web UI
EXPOSE 8501

# Create volume for code files
VOLUME ["/workspace"]

# Default command runs the web UI
CMD ["streamlit", "run", "Backend/ui/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
