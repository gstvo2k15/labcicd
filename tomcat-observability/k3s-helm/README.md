# Tomcat 10.1 / JDK 17 en k3s con Prometheus, Grafana y Loki

Guía paso a paso para ejecutar manualmente en `rocky9vm01` (Rocky Linux, Bash).
Este documento no instala nada automáticamente. Usa Helm para los backends y
Kustomize para Tomcat. Es una alternativa al laboratorio de `../kubernetes/`;
no ejecutes ambos si tu VM no tiene recursos para duplicarlos.

## 1. Elección de logs y arquitectura

Recomiendo **Loki + Grafana Alloy** para este laboratorio de un nodo.
Prometheus recoge métricas; Loki almacena logs; Grafana permite consultar ambos.
Alloy lee los logs de los contenedores a través de la API de Kubernetes.

| Solución | Cuándo elegirla |
| --- | --- |
| Loki | Logs operativos, filtros por etiquetas y búsqueda de texto con LogQL, integración con Grafana. Es la opción de esta guía. |
| OpenSearch | Necesitas indexación del contenido, búsquedas y análisis avanzados de documentos; requiere gestionar también índices, seguridad y su interfaz. |

Loki indexa etiquetas en lugar de indexar todo el contenido del log:
[documentación de Loki](https://grafana.com/docs/loki/latest/get-started/overview/).
El chart predeterminado de OpenSearch despliega tres nodos y su documentación
recomienda al menos 8 GiB disponibles para ese despliegue:
[OpenSearch con Helm](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/helm/).
La recomendación de Loki aquí depende del tamaño y finalidad de tu laboratorio.

```text
Tomcat / JMX exporter <-- ServiceMonitor <-- Prometheus --> Grafana
Tomcat stdout/stderr --> Alloy --> Loki ------------------> Grafana
```

Una réplica por backend, almacenamiento `local-path` y retención de tres días.
No hay alta disponibilidad. Los PVC dependen del disco del nodo y no son backups.
Loki no tiene autenticación en esta configuración: mantén los servicios internos.
Alertmanager queda instalado, pero debes configurar un receptor para enviar avisos.

## 2. Revisar tu k3s antes de añadir carga

Tu salida muestra muchos reinicios y `metrics-server` en `0/1`. Los jobs
`helm-install-*` en `Completed` son normales; los reinicios requieren revisar
la causa. No se puede deducir falta de RAM o un problema TLS solo con esa salida.

```bash
kubectl config current-context
kubectl version
kubectl get nodes -o wide
kubectl describe node rocky9vm01
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -60
kubectl -n kube-system describe pod -l k8s-app=metrics-server
kubectl -n kube-system logs deployment/metrics-server --tail=100
kubectl -n kube-system logs deployment/metrics-server --previous --tail=100
kubectl -n kube-system logs deployment/coredns --previous --tail=100
kubectl get storageclass local-path
free -h
df -h /var/lib/rancher/k3s
journalctl -u k3s -n 100 --no-pager
```

Si `--previous` indica que no existe un contenedor previo, continúa con los logs
actuales. Si `kubectl top nodes` falla, revisa metrics-server; Prometheus usa sus
propios scrapes y no lo necesita para recoger métricas.
No añadas `--kubelet-insecure-tls` sin confirmar antes un error de certificados.

Como orientación para este laboratorio, reserva unos 4 vCPU, 8 GiB de RAM y
20 GiB libres de disco para imágenes y datos; ajusta según el consumo real.
Los PVC solicitan 13 GiB en total. `local-path` no impone necesariamente cuotas
por volumen: vigila el espacio del disco. Instala Helm 3.19+ o Helm 4, kubectl,
Docker para construir la imagen y herramientas `curl`/`base64`.
El chart de Prometheus fijado aquí declara Kubernetes >=1.25; revisa tu versión
antes de continuar.

## 3. Construir e importar la imagen de Tomcat

Desde la raíz de este repositorio, en una máquina con Docker:

```bash
docker build -t lab/tomcat-alpine-jdk17:10.1.61 tomcat-observability/dockercompose/tomcat
docker save lab/tomcat-alpine-jdk17:10.1.61 -o /tmp/tomcat-observability.tar
```

La imagen existente del repositorio contiene Tomcat 10.1.61, JDK 17 y el agente
JMX exporter. Si construyes fuera de la VM, copia el archivo:

```bash
scp /tmp/tomcat-observability.tar root@rocky9vm01:/tmp/
```

En el nodo k3s:

```bash
sudo k3s ctr images import /tmp/tomcat-observability.tar
sudo k3s ctr images list | grep tomcat-alpine
```

Para varios nodos, importa en todos ellos o publica la imagen en un registry y
cambia `image` en el Deployment. Aquí se usa `IfNotPresent` para la imagen importada.
No se activa el agente OpenTelemetry: esta guía cubre métricas JMX y logs.

## 4. Crear los archivos de configuración

En la VM, crea un directorio de trabajo. Todos los comandos restantes parten de él:

```bash
mkdir -p ~/tomcat-k3s-guide/{values,tomcat}
cd ~/tomcat-k3s-guide
```

Ejecuta los siguientes bloques para crear los archivos. Los delimitadores entre
comillas evitan que Bash expanda las variables y patrones del contenido.

### `values/prometheus.yaml`

```bash
cat > values/prometheus.yaml <<'EOF'
fullnameOverride: monitoring
kubeEtcd:
  enabled: false
kubeControllerManager:
  enabled: false
kubeScheduler:
  enabled: false
kubeProxy:
  enabled: false
defaultRules:
  rules:
    etcd: false
    kubeSchedulerAlerting: false
    kubeSchedulerRecording: false
    kubeControllerManager: false
    kubeProxy: false
grafana:
  persistence:
    enabled: true
    storageClassName: local-path
    size: 2Gi
  resources:
    requests: {cpu: 100m, memory: 128Mi}
    limits: {memory: 512Mi}
  additionalDataSources:
    - name: Loki
      uid: loki
      type: loki
      access: proxy
      url: http://loki-gateway.monitoring.svc.cluster.local
      jsonData:
        maxLines: 1000
prometheus:
  prometheusSpec:
    retention: 3d
    retentionSize: 4GB
    resources:
      requests: {cpu: 250m, memory: 512Mi}
      limits: {memory: 1536Mi}
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: local-path
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 5Gi
alertmanager:
  alertmanagerSpec:
    resources:
      requests: {cpu: 25m, memory: 64Mi}
      limits: {memory: 256Mi}
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: local-path
          accessModes: [ReadWriteOnce]
          resources:
            requests:
              storage: 1Gi
EOF
```

### `values/loki.yaml`

```bash
cat > values/loki.yaml <<'EOF'
deploymentMode: SingleBinary
loki:
  auth_enabled: false
  commonConfig:
    replication_factor: 1
  schemaConfig:
    configs:
      - from: "2024-04-01"
        store: tsdb
        object_store: filesystem
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
  storage:
    type: filesystem
  limits_config:
    retention_period: 72h
  compactor:
    retention_enabled: true
    delete_request_store: filesystem
singleBinary:
  replicas: 1
  resources:
    requests: {cpu: 100m, memory: 256Mi}
    limits: {memory: 768Mi}
  persistence:
    enabled: true
    storageClass: local-path
    size: 5Gi
read:
  replicas: 0
write:
  replicas: 0
backend:
  replicas: 0
chunksCache:
  enabled: false
resultsCache:
  enabled: false
lokiCanary:
  enabled: false
test:
  enabled: false
minio:
  enabled: false
EOF
```

### `values/alloy.yaml`

```bash
cat > values/alloy.yaml <<'EOF'
controller:
  type: deployment
  replicas: 1
alloy:
  resources:
    requests: {cpu: 50m, memory: 128Mi}
    limits: {memory: 384Mi}
  configMap:
    content: |
      discovery.kubernetes "tomcat" {
        role = "pod"
        namespaces {
          names = ["tomcat-helm"]
        }
      }
      discovery.relabel "tomcat" {
        targets = discovery.kubernetes.tomcat.targets
        rule {
          source_labels = ["__meta_kubernetes_pod_label_app"]
          regex = "tomcat"
          action = "keep"
        }
        rule {
          source_labels = ["__meta_kubernetes_namespace"]
          target_label = "namespace"
        }
        rule {
          source_labels = ["__meta_kubernetes_pod_name"]
          target_label = "pod"
        }
        rule {
          source_labels = ["__meta_kubernetes_pod_container_name"]
          target_label = "container"
        }
        rule {
          target_label = "app"
          replacement = "tomcat"
        }
      }
      loki.source.kubernetes "tomcat" {
        targets = discovery.relabel.tomcat.output
        forward_to = [loki.write.local.receiver]
      }
      loki.write "local" {
        endpoint {
          url = "http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push"
        }
      }
EOF
```

### `tomcat/namespace.yaml`

```bash
cat > tomcat/namespace.yaml <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: tomcat-helm
EOF
```

### `tomcat/jmx.yaml`

```bash
cat > tomcat/jmx.yaml <<'EOF'
startDelaySeconds: 10
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: 'Catalina<type=GlobalRequestProcessor, name="([^"]+)"><>(requestCount|errorCount|processingTime|bytesReceived|bytesSent):'
    name: tomcat_$2_total
    type: COUNTER
    labels:
      connector: "$1"
  - pattern: 'Catalina<type=ThreadPool, name="([^"]+)"><>(currentThreadCount|currentThreadsBusy|maxThreads):'
    name: tomcat_threadpool_$2
    type: GAUGE
    labels:
      connector: "$1"
  - pattern: 'java.lang<type=Memory><HeapMemoryUsage>(used|committed|max):'
    name: jvm_heap_$1_bytes
    type: GAUGE
EOF
```

### `tomcat/server.xml`

```bash
cat > tomcat/server.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Server port="-1">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <Service name="Catalina">
    <Connector port="8080" protocol="HTTP/1.1" connectionTimeout="20000" />
    <Engine name="Catalina" defaultHost="localhost">
      <Host name="localhost" appBase="webapps" unpackWARs="true" autoDeploy="false">
        <Valve className="org.apache.catalina.valves.AccessLogValve"
               directory="/dev" prefix="stdout" suffix="" rotatable="false"
               buffered="false" pattern="%h %l %u %t &quot;%r&quot; %s %b %D" />
      </Host>
    </Engine>
  </Service>
</Server>
EOF
```

### `tomcat/deployment.yaml`

```bash
cat > tomcat/deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tomcat
spec:
  replicas: 1
  selector:
    matchLabels: {app: tomcat}
  template:
    metadata:
      labels: {app: tomcat}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
      containers:
        - name: tomcat
          image: lab/tomcat-alpine-jdk17:10.1.61
          imagePullPolicy: IfNotPresent
          env:
            - name: CATALINA_OPTS
              value: >-
                -Xms128m -Xmx384m
                -Dcom.sun.management.jmxremote
                -javaagent:/opt/agents/jmx_prometheus_javaagent.jar=0.0.0.0:9404:/etc/tomcat/jmx.yaml
          ports:
            - {name: http, containerPort: 8080}
            - {name: metrics, containerPort: 9404}
          resources:
            requests: {cpu: 100m, memory: 256Mi}
            limits: {memory: 768Mi}
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: [ALL]
          startupProbe:
            httpGet: {path: /, port: http}
            failureThreshold: 30
            periodSeconds: 5
          readinessProbe:
            httpGet: {path: /, port: http}
            periodSeconds: 10
          livenessProbe:
            httpGet: {path: /, port: http}
            periodSeconds: 20
          volumeMounts:
            - {name: config, mountPath: /etc/tomcat, readOnly: true}
            - name: config
              mountPath: /opt/tomcat/conf/server.xml
              subPath: server.xml
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: tomcat-config
EOF
```

### `tomcat/service.yaml`

```bash
cat > tomcat/service.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: tomcat
  labels: {app: tomcat}
spec:
  selector: {app: tomcat}
  ports:
    - {name: http, port: 8080, targetPort: http}
    - {name: metrics, port: 9404, targetPort: metrics}
EOF
```

### `tomcat/servicemonitor.yaml`

```bash
cat > tomcat/servicemonitor.yaml <<'EOF'
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tomcat
  labels:
    release: monitoring
spec:
  selector:
    matchLabels: {app: tomcat}
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
EOF
```

### `tomcat/kustomization.yaml`

```bash
cat > tomcat/kustomization.yaml <<'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: tomcat-helm
resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - servicemonitor.yaml
configMapGenerator:
  - name: tomcat-config
    files:
      - jmx.yaml
      - server.xml
EOF
```

El `server.xml` envía el access log HTTP a `/dev/stdout`; los logs de JUL de
Tomcat también salen por consola con la configuración de la imagen. Tu aplicación
debe escribir sus logs a stdout/stderr: Alloy no recoge archivos privados dentro
del contenedor. Este colector filtra exclusivamente los pods `app=tomcat` del
namespace `tomcat-helm`. La lectura por API evita montar el disco del nodo, a
cambio de carga adicional en kubelet:
[referencia de Alloy](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.kubernetes/).

Se deshabilitan los scrapes de etcd, scheduler, controller-manager y kube-proxy
porque esta guía no configura sus endpoints en k3s. Esto limita su observabilidad;
no impide observar nodos, pods, kubelet ni la aplicación.

## 5. Instalar los charts con Helm

Versiones fijadas y consultadas en el repositorio oficial: kube-prometheus-stack
`92.10.1`, Loki `7.3.0` y Alloy `1.13.1`. Revisa las notas de actualización antes
de cambiar versiones, especialmente las CRD de Prometheus Operator.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Comprobación local de plantillas; todavía no instala recursos.
helm template monitoring prometheus-community/kube-prometheus-stack --version 92.10.1 -n monitoring -f values/prometheus.yaml > /tmp/prometheus-rendered.yaml
helm template loki grafana/loki --version 7.3.0 -n monitoring -f values/loki.yaml > /tmp/loki-rendered.yaml
helm template alloy grafana/alloy --version 1.13.1 -n monitoring -f values/alloy.yaml > /tmp/alloy-rendered.yaml

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --version 92.10.1 --namespace monitoring --create-namespace \
  -f values/prometheus.yaml --wait --timeout 15m

kubectl wait --for=condition=Established crd/servicemonitors.monitoring.coreos.com --timeout=120s

helm upgrade --install loki grafana/loki \
  --version 7.3.0 --namespace monitoring \
  -f values/loki.yaml --wait --timeout 10m
```

Mantén los nombres de release y namespace: los valores y el ServiceMonitor los
usan para enlazar los componentes. Kube-prometheus-stack ya instala Grafana;
no hace falta otra instancia.

## 6. Desplegar Tomcat con Kustomize y activar Alloy

```bash
kubectl kustomize tomcat/
kubectl apply -f tomcat/namespace.yaml
kubectl apply --dry-run=server -k tomcat/
kubectl apply -k tomcat/
kubectl -n tomcat-helm rollout status deployment/tomcat --timeout=180s

helm upgrade --install alloy grafana/alloy \
  --version 1.13.1 --namespace monitoring \
  -f values/alloy.yaml --wait --timeout 5m

kubectl -n tomcat-helm exec deployment/tomcat -- java -version
kubectl -n tomcat-helm exec deployment/tomcat -- /opt/tomcat/bin/version.sh
kubectl -n monitoring get pods,pvc,svc
kubectl -n tomcat-helm get pods,svc,servicemonitor
```

El label `release: monitoring` permite que Prometheus seleccione el ServiceMonitor.
El nombre del puerto `metrics` debe coincidir entre Service y ServiceMonitor.
Kustomize añade un hash al ConfigMap: cambiarlo y volver a aplicar provoca un
nuevo despliegue que carga la configuración actualizada.

## 7. Acceder y comprobar métricas y logs

Abre una terminal por cada port-forward, desde una máquina con acceso kubectl:

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl -n monitoring port-forward svc/monitoring-prometheus 9090:9090
kubectl -n tomcat-helm port-forward svc/tomcat 8080:8080
```

Grafana: http://localhost:3000, usuario `admin`. Obtén la contraseña generada:

```bash
kubectl -n monitoring get secret monitoring-grafana -o jsonpath='{.data.admin-password}' | base64 --decode; echo
```

Si ejecutas los port-forward en la VM y navegas desde otro equipo, crea un túnel
SSH desde ese equipo; no necesitas abrir NodePorts ni cambiar Traefik:

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 -L 8080:127.0.0.1:8080 root@rocky9vm01
```

Genera tráfico en otra terminal:

```bash
for i in $(seq 1 30); do curl -fsS http://localhost:8080/ > /dev/null; done
kubectl -n tomcat-helm logs deployment/tomcat --tail=30
```

En http://localhost:9090/targets debe aparecer el target de Tomcat en `UP`.
Espera uno o dos intervalos de scrape. Consulta estas expresiones en Prometheus
o en Grafana Explore, seleccionando la fuente Prometheus:

```promql
up{namespace="tomcat-helm"}
rate(tomcat_requestcount_total[5m])
rate(tomcat_errorcount_total[5m])
tomcat_threadpool_currentthreadsbusy
jvm_heap_used_bytes
```

Si no aparece una familia, inspecciona primero los nombres que emite el exporter:

```bash
kubectl -n tomcat-helm port-forward svc/tomcat 9404:9404
# En otra terminal:
curl -fsS http://localhost:9404/metrics | grep -E 'tomcat_|jvm_heap_|jmx_scrape'
```

En Grafana > Explore selecciona **Loki**, rango de tiempo éltimos 15 minutos:

```logql
{namespace="tomcat-helm", app="tomcat"}
{namespace="tomcat-helm", app="tomcat"} |= "GET /"
{namespace="tomcat-helm", app="tomcat"} |~ "ERROR|SEVERE|Exception"
```

La fuente Loki queda provisionada automáticamente. Los dashboards Kubernetes
incluidos en el stack muestran nodos y workloads. Para Tomcat crea paneles con
las consultas anteriores; los dashboards que esperan otras métricas pueden
necesitar adaptar sus consultas a estas reglas JMX.

## 8. Diagnóstico y mantenimiento

```bash
helm list -n monitoring
kubectl -n monitoring get events --sort-by=.lastTimestamp | tail -40
kubectl -n monitoring get pvc
kubectl -n tomcat-helm describe pod -l app=tomcat
kubectl -n tomcat-helm logs deployment/tomcat --previous
kubectl -n monitoring logs deployment/alloy -c alloy --tail=100
kubectl -n monitoring logs statefulset/loki --tail=100
kubectl -n monitoring get prometheus monitoring-prometheus -o yaml
kubectl -n tomcat-helm get servicemonitor tomcat -o yaml
```

- `Pending`: revisa eventos, RAM solicitada y PVC `local-path`.
- `ImagePullBackOff`: verifica que importaste la imagen con exactamente el mismo nombre.
- `OOMKilled`: revisa consumo y aumenta memoria de la VM o ajusta límites y heap.
- Target ausente: revisa label `release: monitoring`, selector del Service y puerto `metrics`.
- Target `DOWN`: revisa logs del agente, puerto 9404 y conectividad entre pods.
- Loki sin logs: confirma primero `kubectl logs`, después errores de Alloy y Loki.
- Un timeout de Helm puede dejar una release instalada parcialmente; inspecciona
  pods y eventos, corrige la causa y repite `helm upgrade --install`.

Para actualizar, edita los archivos y repite los comandos de Helm y
`kubectl apply -k tomcat/`. Para una imagen reconstruida con la misma etiqueta,
reimpórtala y ejecuta `kubectl -n tomcat-helm rollout restart deployment/tomcat`.
Usar una etiqueta nueva por construcción evita ambigüedades.

Esta es una configuración de laboratorio. Para producción añade TLS,
autenticación, control de acceso, copias de seguridad, almacenamiento adecuado,
receptores de alertas y capacidad/retención dimensionadas. Los logs aún no enviados
pueden perderse con rotaciones o fallos; no hay garantía de entrega exactamente una vez.

## 9. Retirar el laboratorio (solo cuando quieras)

```bash
helm uninstall alloy -n monitoring
kubectl delete -k tomcat/
helm uninstall loki -n monitoring
helm uninstall monitoring -n monitoring
kubectl -n monitoring get pvc
```

Borrar `tomcat/` también borra el namespace `tomcat-helm` y todo lo que contenga.
Las releases pueden conservar PVC y CRD; inspecciónalos antes de eliminarlos.
No borres el namespace `monitoring` ni sus PVC si quieres conservar los datos.

## Referencias

- [kube-prometheus-stack en Artifact Hub](https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack)
- [Valores oficiales de kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Chart oficial de Loki](https://github.com/grafana/loki/tree/main/production/helm/loki)
- [Chart oficial de Alloy](https://github.com/grafana/alloy/tree/main/operations/helm/charts/alloy)
- [OpenSearch en Artifact Hub](https://artifacthub.io/packages/helm/opensearch-project-helm-charts/opensearch)

Validación durante la preparación: se renderizaron los charts de Prometheus y
Alloy, y se consultó la versión publicada de Loki. Esta guía no se ha ejecutado
contra `rocky9vm01`; valida las plantillas y los recursos con los comandos previos
antes de instalar.
