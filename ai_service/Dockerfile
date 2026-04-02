# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# HF Spaces requirement: Create user and set permissions
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Install standard dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code
COPY . /code

# Give permissions to the new user
RUN chown -R user:user /code
USER user

# Hugging Face Spaces exposes port 7860 by default
EXPOSE 7860

# Run uvicorn server on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
