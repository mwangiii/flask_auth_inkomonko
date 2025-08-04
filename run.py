from app import app
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
