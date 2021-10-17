FROM python:3

# Set working space
WORKDIR /usr/src/app

# Install dependencies
RUN apt-get update \
    # Prevent endless waiting
    && DEBIAN_FRONTEND=noninteractive \
    # Set UTC as timezone
    && ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    # Install APT packages
    && apt-get install -y --fix-missing wkhtmltopdf \
    # Remove tmp files
    && apt-get clean && rm -rf /tmp/* /var/tmp/* \
    # Add PiWheels support
    && echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf \
    # Upgrade PIP 
    && python3 -m pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy app
COPY . .

# Create folder
RUN mkdir out

# Start the bot
CMD python3 -u bot.py