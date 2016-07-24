FROM python:alpine
MAINTAINER Danilo Bargen <mail@dbrgn.ch>

# Code directory
RUN mkdir /code
WORKDIR /code

# Install dependencies
ADD requirements.txt /code/
RUN pip install -r /code/requirements.txt

# Add code
ADD logger.py config.json run.sh /code/

# Create user
RUN adduser -D logger \
    && chown -R logger:logger /code
USER logger

# Entry point
CMD ["sh", "run.sh"]
