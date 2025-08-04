from app import create_app
from prometheus_flask_exporter import PrometheusMetrics

app = create_app()

# Attach metrics BEFORE routes get hit
metrics = PrometheusMetrics(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
