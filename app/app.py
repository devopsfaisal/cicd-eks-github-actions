import os
import socket
import time
from flask import Flask, render_template, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['endpoint']
)

START_TIME = time.time()


def get_metadata():
    """Retrieve environment and host metadata."""
    return {
        "hostname": socket.gethostname(),
        "pod_ip": os.getenv("POD_IP", "127.0.0.1"),
        "node_name": os.getenv("NODE_NAME", "local-dev-node"),
        "namespace": os.getenv("POD_NAMESPACE", "production"),
        "app_version": os.getenv("APP_VERSION", "v1.0.0"),
        "git_commit": os.getenv("GIT_COMMIT_SHA", "HEAD")[:7],
        "environment": os.getenv("ENVIRONMENT", "production"),
        "region": os.getenv("AWS_REGION", "ap-south-1"),
        "uptime_seconds": int(time.time() - START_TIME)
    }


@app.before_request
def before_request():
    pass


@app.route("/")
def index():
    start = time.time()
    metadata = get_metadata()
    REQUEST_COUNT.labels(method='GET', endpoint='/', status_code='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    return render_template("index.html", data=metadata)


@app.route("/healthz")
def healthz():
    """Liveness probe - checks if app process is alive."""
    REQUEST_COUNT.labels(method='GET', endpoint='/healthz', status_code='200').inc()
    return jsonify(status="healthy", uptime=int(time.time() - START_TIME)), 200


@app.route("/readyz")
def readyz():
    """Readiness probe - checks if app is ready to receive traffic."""
    REQUEST_COUNT.labels(method='GET', endpoint='/readyz', status_code='200').inc()
    return jsonify(status="ready", timestamp=time.time()), 200


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
