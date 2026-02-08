# 1. Use a specific, stable Python version (Slim is faster/smaller)
FROM python:3.10-slim

# 2. Set Environment Variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr (Instant Logs!)
ENV PYTHONUNBUFFERED=1
# Fixes the GitPython error permanently inside the container
ENV GIT_PYTHON_REFRESH=quiet

# 3. Install System Dependencies
# git: For the updater
# ffmpeg: For future media handling
# build-essential: For compiling certain python libraries if needed
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory
WORKDIR /app

# 5. Copy Requirements first (Docker Cache Optimization)
# This makes re-deploying faster if you only changed code, not libraries
COPY requirements.txt .

# 6. Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of the application code
COPY . .

# 8. Command to start the bot
# We use 'sh -c' to ensure environment variables are loaded correctly
CMD ["python", "Ryan.py"]