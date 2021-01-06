FROM python:3

# Set working space
WORKDIR /usr/src/app

# Install requirements
RUN ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime && \
    apt-get update && apt-get install -y wkhtmltopdf
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Create folder
RUN mkdir out

# Start the bot
CMD python -u bot.py