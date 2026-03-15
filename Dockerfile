# Use an official, lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project into the container
COPY . .

# Create a startup script to run both servers simultaneously
# FastAPI runs in the background (&) on port 8000
# Streamlit runs in the foreground on port 7860 (Hugging Face's required port)
RUN echo '#!/bin/bash\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
sleep 5\n\
streamlit run app.py --server.port 7860 --server.address 0.0.0.0\n\
' > start.sh

# Make the startup script executable
RUN chmod +x start.sh

# Expose the port that Hugging Face Spaces looks for
EXPOSE 7860

# Command to trigger the startup script when the container boots
CMD ["./start.sh"]