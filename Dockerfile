FROM python:3-alpine

# Set working space
WORKDIR /usr/src/app

# Install dependencies
RUN apk update \
    # Set UTC as timezone
    && ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    # Install APT packages
    && apk add \
        gcc build-base freetype-dev libpng-dev openblas-dev \
        py3-numpy py3-pandas py3-pillow py3-matplotlib \
        wkhtmltopdf \
    # Remove tmp files
    && rm -rf /tmp/* /var/tmp/* \
    # Add PiWheels support
    && echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf \
    # Upgrade PIP 
    && python3 -m pip install --no-cache-dir --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create folder
RUN mkdir out

# Start the bot
CMD python3 -u bot.py