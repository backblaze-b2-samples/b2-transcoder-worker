# B2 Transcoder Worker

The Backblaze B2 Transcoder Proof-of-Concept comprises this lightweight Flask worker app and a web app implemented with Django and JavaScript. Together, they implement a simple video hosting site. 

See the B2 Transcoder Web App for for an explanation of how the two apps interoperate.

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
    BUCKET_NAME="<your B2 bucket>"
    ```

## Run the Worker App

* `flask run` to run the app in the Flask development server.

    You may change the interface and port to which the app binds with the `-h/--host` and `-p/--port` options. For example, to listen on the standard HTTP port on all interfaces, you would use:

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

Feel free to fork this repository and submit a pull request if you make an interesting change!