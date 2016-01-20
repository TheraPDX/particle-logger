"""
A small Python 3 script to check the `temperature` variable Particle Photons
and log them to a Grafana board.
"""

import json
import os
import sys

import requests
import influxdb


# Helper functions

env = os.environ.get


def require_env(name):
    value = env(name)
    if not value:
        raise ValueError('Missing %s env variable' % name)
    return value


# Configuration

INFLUXDB_HOST = require_env('INFLUXDB_HOST')
INFLUXDB_PORT = int(env('INFLUXDB_PORT', 8086))
INFLUXDB_USER = require_env('INFLUXDB_USER')
INFLUXDB_PASSWORD = require_env('INFLUXDB_PASSWORD')
INFLUXDB_DATABASE = require_env('INFLUXDB_DATABASE')

PARTICLE_CLIENT_ID = require_env('PARTICLE_CLIENT_ID')
PARTICLE_CLIENT_SECRET = require_env('PARTICLE_CLIENT_SECRET')
PARTICLE_REFRESH_TOKEN = require_env('PARTICLE_REFRESH_TOKEN')


# Logging functionality

def collect_metric(measurement, tags, value):
    """
    Send a measurement to InfluxDB.

    Args:
        measurement (str):
            The name of the measurement.
        tags (dict):
            Tags for the measurement.
        value (int or float):
            The value to log. Should be a numeric value.

    """
    data = [{
        'measurement': measurement,
        'tags': tags,
        'fields': {
            'value': value,
        }
    }]
    client = influxdb.InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT,
                                     INFLUXDB_USER, INFLUXDB_PASSWORD,
                                     INFLUXDB_DATABASE)
    print('INFLUX: Processing device %s' % name)
    success = client.write_points(data)
    if success is not True:
        raise RuntimeError('Could not send metric to InfluxDB')


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

    # Read config file
    devices = get_devices()

    # For each device, fetch and upload the variables
    access_token = get_access_token()
    for name, variables in devices.items():
        print('MAIN: Processing device %s' % name)
        for conf in variables:
            variable = conf['variable']
            value = fetch_variable(name, variable, access_token)
            if value is None:
                print('MAIN: Could not fetch variable %s for device %s' % (variable, name))
            else:
                collect_metric(conf['measurement'], conf['tags'], value)
