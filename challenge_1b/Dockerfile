# Use a lightweight Python base image that supports AMD64 architecture
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and requirements file into the container
COPY document_analyst.py .
COPY requirements.txt .

# Copy the lang_data directory into the container. This must exist locally.
COPY lang_data/ /app/lang_data/

# Install Python dependencies specified in requirements.txt
# --no-cache-dir reduces the size of the Docker image
# Install Janome and Pecab specifically AND run their internal setup for dictionaries
RUN pip install --no-cache-dir -r requirements.txt \
    && python -c "from janome.tokenizer import Tokenizer; t = Tokenizer()" \
    && python -c "from pecab import PeCab; p = PeCab()"

# Create the input and output directories as expected by the application
# PDFs will be placed in /app/input/PDFs, and input JSON in /app/input
# output JSON will be written to /app/output (which is mounted back to /app/input for this challenge)
RUN mkdir -p /app/input/PDFs

# Define the default command to run the application.
# When the Docker container starts, it will execute this command.
# The Python script is designed to automatically find challenge1b_input.json
# and PDFs in /app/input/PDFs and write the result to /app/input (the mounted folder).
CMD ["python", "document_analyst.py"]
