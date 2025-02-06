FROM streamlit/streamlit-lancer:latest

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install ollama model - deepseek-r1:1.5b and start Ollama server
RUN apt-get update && apt-get install -y wget curl  # Install wget and curl if not already present
RUN curl -fsSL https://apt.repos.ollama.ai/ollama.gpg | gpg --dearmor -o /usr/share/keyrings/ollama.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/ollama.gpg] https://apt.repos.ollama.ai/ bookworm main" > /etc/apt/sources.list.d/ollama.list
RUN apt-get update && apt-get install -y ollama
RUN ollama pull deepseek-r1:1.5b

# Start Ollama server in the background
CMD ollama serve & streamlit run app.py