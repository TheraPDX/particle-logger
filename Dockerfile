FROM python:alpine
MAINTAINER Danilo Bargen <mail@dbrgn.ch>

# Install dependencies
RUN pip install "requests<=3"

# Code directory
RUN mkdir /code
WORKDIR /code

# Add code
ADD logger.py config.json run.sh /code/

# Create user
RUN adduser -D logger \
    && chown -R logger:logger /code
USER logger

# Entry point
CMD ["sh", "run.sh"]
