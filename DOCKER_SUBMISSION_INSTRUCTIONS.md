# FixGoblin Docker Image - Submission Instructions

## What's Included
- **File**: `fixgoblin-docker-image.tar.gz`
- **Size**: ~662 MB (compressed)
- **Image Name**: `fixgoblin:latest`

## Prerequisites
- Docker Desktop or Docker Engine installed
- At least 3 GB of free disk space

## How to Load and Run the Docker Image

### Step 1: Load the Docker Image
```bash
# Extract the compressed file
gunzip fixgoblin-docker-image.tar.gz

# Load the image into Docker
docker load -i fixgoblin-docker-image.tar
```

### Step 2: Verify the Image
```bash
docker images fixgoblin
```
You should see: `fixgoblin:latest`

### Step 3: Run the Container

**Option A: Run with Web UI (Streamlit)**
```bash
docker run -p 8501:8501 fixgoblin:latest
```
Then open your browser to: http://localhost:8501

**Option B: Run with CLI (Interactive)**
```bash
docker run -it fixgoblin:latest /bin/bash
# Inside container, run:
python fixgoblin.py --help
```

**Option C: Run with Volume Mount (to debug your own code)**
```bash
docker run -p 8501:8501 -v $(pwd)/workspace:/workspace fixgoblin:latest
```

### Step 4: Test the Application
1. Access the web UI at http://localhost:8501
2. Upload a buggy code file or paste code directly
3. Click "Debug & Fix" to see FixGoblin in action

## Quick Test Example
```bash
# Start the container
docker run -p 8501:8501 fixgoblin:latest

# Open browser to http://localhost:8501
# The Streamlit UI should load
```

## Supported Languages
- Python
- C/C++
- Java
- JavaScript
- Go

## Features
- Autonomous debugging
- Multi-language support
- Syntax fixing
- Logical analysis
- Test case validation
- Patch generation

## Troubleshooting

**Port already in use?**
```bash
docker run -p 9999:8501 fixgoblin:latest
# Then access: http://localhost:9999
```

**Container won't start?**
```bash
docker logs fixgoblin
```

**Remove container after stopping:**
```bash
docker stop fixgoblin
docker rm fixgoblin
```

## Technical Details
- **Base Image**: Ubuntu 22.04
- **Python**: 3.10
- **Languages**: Python, C++, Java, JavaScript, Go
- **Web Framework**: Streamlit
- **Port**: 8501 (default)

## Contact
For questions or issues, refer to the main README.md in the source repository.

---
**Built with FixGoblin** - Multi-Language Autonomous Debugging System
