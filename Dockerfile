# Start with a base image that supports multiple architectures
FROM nikolaik/python-nodejs:latest

# Set working directory
WORKDIR /app

# Copy the entire project directory into the container
COPY . .

# Install Node.js dependencies
RUN cd web && npm install

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Expose any necessary ports
EXPOSE 3000

# Command to run your application
#CMD ["bash", "-c", "cd /app/server && python3 main.py && sleep 7 && cd /app/web && node app.js"]
#CMD ["node", "/app/web/app.js"]
#CMD ["node", "/app/web/app.js"]
# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
