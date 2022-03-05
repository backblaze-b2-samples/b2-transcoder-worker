# B2 Transcoder Worker

The [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) Transcoder Proof-of-Concept comprises this lightweight [Flask](https://palletsprojects.com/p/flask/) worker app and a web app implemented with [Django](https://www.djangoproject.com) with a JavaScript front end. Together, they implement a simple video hosting site. 

See the [B2 Transcoder Web App](https://github.com/Backblaze-B2-Samples/b2-transcoder-web-app) for for an explanation of how the two apps interoperate.

## Prerequisites

* [Python 3.9.2](https://www.python.org/downloads/release/python-392/) (other Python versions _may_ work) and `pip`
* [`ffmpeg`](https://www.ffmpeg.org/download.html)

## Installation

* Clone this repository and `cd` into the local repository directory.

* `pip install -r requirements`

## Configuration

* Create a `.env` file or set environment variables with your configuration:

    ```bash
    B2_ENDPOINT_URL="<for example: https://s3.us-west-001.backblazeb2.com>"
    B2_APPLICATION_KEY_ID="<your B2 application key ID>"
    B2_APPLICATION_KEY="<your B2 application key>"
    BUCKET_NAME="<your private B2 bucket, for uploaded videos>"
    ```

## Run the Worker App

* `flask run` to run the app in the Flask development server.

    You may change the interface and port to which the worker app binds with the `-h/--host` and `-p/--port` options. For example, to listen on the standard HTTP port on all interfaces, you would use:

    ```bash
    flask run -h 0.0.0.0 -p 80
    ```

## Install, Configure and Run the Web App

* Follow the instructions to install and configure the transcoder web app.

* Configure the web app with the worker's endpoint URL via the `.env` file or an environment variable:

    ```bash
    TRANSCODER_WEBHOOK=http://<worker IP address>:<worker port>/videos
    ```

* Run the web app.

## Caveats

Note that this is a proof-of-concept system! To run a similar system in production, you would need to make several changes, including:

* Using a message queue such as [Apache Kafka](https://kafka.apache.org) or [RabbitMQ](https://www.rabbitmq.com) rather than HTTP POST notifications.
* Running the apps from a WSGI server such as [Green Unicorn](http://gunicorn.org/) or [Apache Web Server](https://httpd.apache.org) with [`mod_wsgi`](https://github.com/GrahamDumpleton/mod_wsgi).

Feel free to fork this repository and submit a pull request if you make an interesting change!