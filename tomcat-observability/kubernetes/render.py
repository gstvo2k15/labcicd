"""Render Kubernetes resources from the Compose lab's canonical configuration."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'dockercompose'
NS = 'tomcat-observability'
resources = []


def resource(kind, name, **fields):
    obj = dict(apiVersion='apps/v1' if kind == 'Deployment' else 'v1',
               kind=kind, metadata=dict(name=name, namespace=NS), **fields)
    resources.append(obj)
    return obj


def config(name, files):
    resource('ConfigMap', name, data={key: (SOURCE / path).read_text(encoding='utf-8')
                                    for key, path in files.items()})


def mount(name, path, sub=None, readonly=False):
    result = dict(name=name, mountPath=path, readOnly=readonly)
    if sub:
        result['subPath'] = sub
    return result


def container(name, image, uid, port, path, memory, args=None, mounts=None, env=None):
    probe = dict(httpGet=dict(path=path, port=port), periodSeconds=10, timeoutSeconds=5)
    c = dict(name=name, image=image, imagePullPolicy='IfNotPresent',
             securityContext=dict(runAsNonRoot=True, runAsUser=uid, runAsGroup=uid,
                                  readOnlyRootFilesystem=True, allowPrivilegeEscalation=False,
                                  capabilities=dict(drop=['ALL'])),
             resources=dict(requests=dict(cpu='50m', memory='64Mi'),
                            limits=dict(cpu='1', memory=memory)),
             readinessProbe=probe, livenessProbe=probe,
             startupProbe={**probe, 'failureThreshold': 60},
             volumeMounts=mounts or [])
    if args:
        c['args'] = args
    if env:
        c['env'] = [dict(name=k, value=v) for k, v in env.items()]
    return c


def deployment(name, containers, volumes, uid, ports, storage=True):
    if storage:
        resource('PersistentVolumeClaim', name + '-data', spec=dict(
            accessModes=['ReadWriteOnce'], storageClassName='local-path',
            resources=dict(requests=dict(storage='2Gi'))))
        volumes.append(dict(name='data', persistentVolumeClaim=dict(claimName=name + '-data')))
    resource('Deployment', name, spec=dict(replicas=1, strategy=dict(type='Recreate'),
        selector=dict(matchLabels=dict(app=name)), template=dict(metadata=dict(labels=dict(app=name)),
        spec=dict(automountServiceAccountToken=False,
                  securityContext=dict(fsGroup=uid, seccompProfile=dict(type='RuntimeDefault')),
                  containers=containers, volumes=volumes))))
    resource('Service', name, spec=dict(selector=dict(app=name), ports=[
        dict(name='port-' + str(p), port=p, targetPort=p) for p in ports]))


resource('Namespace', NS)
config('telemetry-config', {name: 'config/' + name for name in [
    'jmx-exporter.yaml', 'otel-collector.yaml', 'prometheus.yaml', 'alerts.yaml',
    'alertmanager.yaml', 'loki.yaml', 'tempo.yaml']})
config('grafana-provisioning', {
    'datasources.yaml': 'grafana/provisioning/datasources/datasources.yaml',
    'dashboards.yaml': 'grafana/provisioning/dashboards/dashboards.yaml'})
config('grafana-dashboard', {'tomcat.json': 'grafana/dashboards/tomcat.json'})

tomcat = container('tomcat', 'lab/tomcat-alpine-jdk17:10.1.61', 10001, 8080, '/', '768Mi',
    mounts=[mount('logs', '/opt/tomcat/logs'), mount('tmp', '/tmp'),
            mount('work', '/opt/tomcat/work'), mount('temp', '/opt/tomcat/temp'),
            mount('config', '/opt/tomcat/conf/jmx-exporter.yaml', 'jmx-exporter.yaml', True)],
    env=dict(JAVA_TOOL_OPTIONS='-javaagent:/opt/agents/opentelemetry-javaagent.jar '
             '-javaagent:/opt/agents/jmx_prometheus_javaagent.jar=0.0.0.0:9404:/opt/tomcat/conf/jmx-exporter.yaml '
             '-XX:MaxRAMPercentage=70', OTEL_SERVICE_NAME='tomcat',
             OTEL_RESOURCE_ATTRIBUTES='deployment.environment.name=lab',
             OTEL_EXPORTER_OTLP_ENDPOINT='http://localhost:4318',
             OTEL_EXPORTER_OTLP_PROTOCOL='http/protobuf', OTEL_METRICS_EXPORTER='otlp',
             OTEL_TRACES_EXPORTER='otlp', OTEL_LOGS_EXPORTER='none',
             OTEL_METRIC_EXPORT_INTERVAL='15000'))
collector = container('otel-collector', 'otel/opentelemetry-collector-contrib:0.163.1',
    10001, 13133, '/', '384Mi', ['--config=/etc/otelcol/config.yaml'],
    [mount('config', '/etc/otelcol/config.yaml', 'otel-collector.yaml', True),
     mount('logs', '/var/log/tomcat', readonly=True), mount('data', '/var/lib/otelcol')])
deployment('tomcat', [tomcat, collector], [dict(name='config', configMap=dict(name='telemetry-config')),
    *[dict(name=n, emptyDir={}) for n in ['logs', 'tmp', 'work', 'temp']]], 10001, [8080, 9404])
resource('Service', 'otel-collector', spec=dict(selector=dict(app='tomcat'),
    ports=[dict(name='metrics', port=9464, targetPort=9464)]))

for name, image, uid, port, ready, memory, args, data_path, files in [
    ('prometheus', 'prom/prometheus:v3.15.0', 65534, 9090, '/-/ready', '512Mi',
     ['--config.file=/etc/prometheus/prometheus.yml', '--storage.tsdb.path=/prometheus',
      '--storage.tsdb.retention.time=7d'], '/prometheus',
     [('prometheus.yaml', '/etc/prometheus/prometheus.yml'), ('alerts.yaml', '/etc/prometheus/alerts.yaml')]),
    ('alertmanager', 'prom/alertmanager:v0.34.1', 65534, 9093, '/-/ready', '128Mi',
     ['--config.file=/etc/alertmanager/alertmanager.yml', '--storage.path=/alertmanager'],
     '/alertmanager', [('alertmanager.yaml', '/etc/alertmanager/alertmanager.yml')]),
    ('loki', 'grafana/loki:3.7.8', 10001, 3100, '/ready', '512Mi',
     ['-config.file=/etc/loki/config.yaml'], '/loki', [('loki.yaml', '/etc/loki/config.yaml')]),
    ('tempo', 'grafana/tempo:2.10.8', 10001, 3200, '/ready', '384Mi',
     ['-config.file=/etc/tempo/config.yaml'], '/var/tempo', [('tempo.yaml', '/etc/tempo/config.yaml')]),
]:
    c = container(name, image, uid, port, ready, memory, args,
                  [mount('data', data_path), mount('tmp', '/tmp'),
                   *[mount('config', path, key, True) for key, path in files]])
    deployment(name, [c], [dict(name='config', configMap=dict(name='telemetry-config')),
                          dict(name='tmp', emptyDir={})], uid,
               [port, 4317] if name == 'tempo' else [port])

grafana = container('grafana', 'grafana/grafana:12.4.13', 472, 3000, '/api/health', '384Mi',
    mounts=[mount('data', '/var/lib/grafana'), mount('tmp', '/tmp'),
            mount('provisioning', '/etc/grafana/provisioning/datasources/datasources.yaml', 'datasources.yaml', True),
            mount('provisioning', '/etc/grafana/provisioning/dashboards/dashboards.yaml', 'dashboards.yaml', True),
            mount('dashboard', '/var/lib/grafana/dashboards', readonly=True)],
    env=dict(GF_USERS_ALLOW_SIGN_UP='false', GF_AUTH_ANONYMOUS_ENABLED='false',
             GF_ANALYTICS_REPORTING_ENABLED='false'))
grafana['env'].append(dict(name='GF_SECURITY_ADMIN_PASSWORD', valueFrom=dict(
    secretKeyRef=dict(name='grafana-admin', key='password'))))
deployment('grafana', [grafana], [dict(name='tmp', emptyDir={}),
    dict(name='provisioning', configMap=dict(name='grafana-provisioning')),
    dict(name='dashboard', configMap=dict(name='grafana-dashboard'))], 472, [3000])

output = json.dumps(dict(apiVersion='v1', kind='List', items=resources), indent=2) + '\n'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
options = parser.parse_args()
target = ROOT / 'resources.json'
if options.check:
    if not target.exists() or target.read_text(encoding='utf-8') != output:
        raise SystemExit('Stale manifests: run python tomcat-observability/kubernetes/render.py')
else:
    target.write_text(output, encoding='utf-8')
