"""
A small Python 3 script to check the `temperature` variable Particle Photons
and log them to a Grafana board.
"""

import json
import os
import socket
import sys
import time

import requests


# Helper functions

env = os.environ.get


def require_env(name):
    value = env(name)
    if not value:
        raise ValueError('Missing %s env variable' % name)
    return value


def now():
    """
    Return the current timestamp as an integer.
    """
    return int(time.time())


# Configuration

GRAPHITE_HOST = require_env('GRAPHITE_HOST')
GRAPHITE_PORT = int(env('GRAPHITE_PORT', 2003))
PARTICLE_CLIENT_ID = require_env('PARTICLE_CLIENT_ID')
PARTICLE_CLIENT_SECRET = require_env('PARTICLE_CLIENT_SECRET')
PARTICLE_REFRESH_TOKEN = require_env('PARTICLE_REFRESH_TOKEN')


# Logging functionality

def collect_metric(name, value, timestamp=None):
    """
    Send a metric to Graphite.

    Args:
        name (str):
            The name of the metric. Use dots for namespacing.
            Example: ``locations.serverroom.temperature``.
        value (int or float):
            The value to log. Should be a numeric value.
        timestamp (int):
            A unix timestamp. Defaults to now.

    """
    data = '%s %s %d\n' % (name, value, timestamp or now())
    print('GRAPHITE: %s' % data.strip())
    sock = socket.socket()
    sock.connect((GRAPHITE_HOST, GRAPHITE_PORT))
    sock.send(data.encode('ascii'))
    sock.close()


# Particle Cloud API related functionality

def get_access_token():
    """
    Get a valid access token.

    TODO: Cache access token.

    """
    # Prepare request
    url = 'https://api.particle.io/oauth/token'
    auth = (PARTICLE_CLIENT_ID, PARTICLE_CLIENT_SECRET)
    data = {'grant_type': 'refresh_token', 'refresh_token': PARTICLE_REFRESH_TOKEN}

    # Send request
    print('PARTICLE: Fetching access token...')
    response = requests.post(url, auth=auth, data=data)
    if response.status_code != 200:
        print('  Could not retrieve access token (HTTP %s)' % response.status_code)
        print('  Are your refresh token and client credentials correct?')
        sys.exit(1)

    # Decode response
    data = response.json()
    return data['access_token']


def fetch_variable(device, variable, access_token):
    """
    Fetch a variable on a device from the Particle Cloud API.

    Args:
        device (str):
            Name or ID of the device to query.
        variable (str):
            Name of the variable to query.
        access_token (str):
            A particle API access token.
    Returns:
        The value returned by the API as a numeric value.

    """
    # Prepare request
    url = 'https://api.particle.io/v1/devices/%s/%s' % (device, variable)
    headers = {'Authorization': 'Bearer %s' % access_token}

    # Send request
    print('PARTICLE: Fetching %s for device %s...' % (variable, device))
    response = requests.get(url, headers=headers)
    if response.status_code == 408:
        print('  Could not fetch variable %s from device %s' % (variable, device))
        print('  Device appears to be offline.')
        return None
    elif response.status_code != 200:
        print('  HTTP %s' % response.status_code)
        print('  Could not fetch variable %s from device %s' % (variable, device))
        print('  Does that device exist, is it yours and does it publish that variable?')
        return None

    # Decode response
    data = response.json()
    return data['result']


def get_devices():
    """
    Open and parse config file.
    """
    with open('config.json', 'r') as f:
        config = json.loads(f.read())
    return config

# Entry point

if __name__ == '__main__':
    devices = get_devices()
    access_token = get_access_token()
    for name, variables in devices.items():
        print('MAIN: Processing device %s' % name)
        for conf in variables:
            variable = conf['variable']
            value = fetch_variable(name, variable, access_token)
            if value is None:
                print('MAIN: Could not fetch variable %s for device %s' % (variable, name))
            else:
                collect_metric(conf['metric_name'], value)
