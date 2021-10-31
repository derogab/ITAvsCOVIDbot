FROM alpine:latest

# Set working space
WORKDIR /usr/src/app

# Install dependencies
RUN apk update \
    # Set UTC as timezone
    && ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    # Install packages
    && apk add \
        build-base freetype-dev libpng-dev openblas-dev \
        python3 py3-pip py3-numpy py3-pandas py3-matplotlib \
        wkhtmltopdf \
    # Remove tmp files
    && rm -rf /tmp/* /var/tmp/* \
    # Add PiWheels support
    && echo "[global]\nextra-index-url=https://www.piwheels.org/simple" >> /etc/pip.conf \
    # Upgrade PIP 
    && python3 -m pip install --no-cache-dir --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install requirements
RUN apk update \
    # Install tmp packages 
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    # Install PIP packages
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    # Delete tmp packages
    && apk del build-deps

# Copy app
COPY . .

# Create folder
RUN mkdir out

# Start the bot
CMD python3 -u bot.py