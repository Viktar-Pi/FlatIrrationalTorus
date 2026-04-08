FROM python:3.9-slim

WORKDIR /app

# Install CLASS and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    gfortran \
    libgsl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "analysis/mcmc_run.py"]
