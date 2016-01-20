# Photon Logger

Log temperatures from Photons to Grafana through InfluxDB.


## Env Vars

The following env variables are required:

- `INFLUXDB_HOST`: The InfluxDB host.
- `INFLUXDB_USER`: The InfluxDB user.
- `INFLUXDB_PASSWORD`: The InfluxDB password.
- `INFLUXDB_DATABASE`: The InfluxDB database.
- `PARTICLE_CLIENT_ID`: A Particle Cloud API OAuth client id.
- `PARTICLE_CLIENT_SECRET`: A Particle Cloud API OAuth client secret.
- `PARTICLE_REFRESH_TOKEN`: A Particle Cloud API refresh token.

The following env variables may be set:

- `INFLUXDB_PORT`: The InfluxDB port. Defaults to `8086`.


## Config file

Adjust `config.json` to your likings.


## Generating a Particle Cloud API token

See docs at https://docs.particle.io/reference/api/#create-an-oauth-client and
https://docs.particle.io/reference/api/#generate-an-access-token.
Replace all values inside `<angle brackets>` with your own values.

Export your credentials:

    $ export PARTICLE_USERNAME=<joe@example.com>
    $ export PARTICLE_PASSWORD=<your-password>

Get an access token:

    $ curl https://api.particle.io/oauth/token \
        -u particle:particle -d grant_type=password \
        -d username="$PARTICLE_USERNAME" -d password="$PARTICLE_PASSWORD"

Create an OAuth client:

    $ curl https://api.particle.io/v1/clients \
        -d name=<client-name> -d type=installed \
        -d access_token=<access-token>

Get a refresh token using your new client:

    $ curl https://api.particle.io/oauth/token \
        -u <client-id>:<client-secret> -d grant_type=password \
        -d username="$PARTICLE_USERNAME" -d password="$PARTICLE_PASSWORD"

You should now have a client id, a client secret and a refresh token.


## Deploying to Docker

Build the image:

    $ docker build -t coredump-ch/photon-logger:latest .

Start the image:

    $ docker run -d \
        -e INFLUXDB_HOST=<host> \
        -e INFLUXDB_USER=<user> \
        -e INFLUXDB_PASSWORD=<password> \
        -e INFLUXDB_DATABASE=<database> \
        -e PARTICLE_CLIENT_ID=<client-id> \
        -e PARTICLE_CLIENT_SECRET=<client-secret> \
        -e PARTICLE_REFRESH_TOKEN=<refresh-token>
        coredump-ch/photon-logger:latest

Or push the container to Docker Hub:

    $ docker push coredump-ch/photon-logger:latest
