FROM alpine:3.14

# Set working space
WORKDIR /usr/src/app

# Install dependencies
RUN apk update --no-cache \
    # Install packages
    && apk add --no-cache \
        tzdata \
        python3 py3-pip py3-numpy py3-pandas py3-matplotlib \
        wkhtmltopdf \
    # Set UTC as timezone
    && ln -snf /usr/share/zoneinfo/Europe/Rome /etc/localtime \
    # Remove tmp files
    && rm -rf /tmp/* /var/tmp/* \
    # Upgrade PIP 
    && python3 -m pip install --no-cache-dir --upgrade pip

# Copy PIP extra index URLs
COPY pip.conf .

# Copy requirements
COPY requirements.txt .

# Install requirements
RUN apk update --no-cache \
    # Install tmp packages 
    && apk add --no-cache --virtual build-deps gcc python3-dev musl-dev build-base freetype-dev libpng-dev openblas-dev \
    # Add PIP extra index URLs
    && mv pip.conf /etc/pip.conf \
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