# labcicd
Basic repo for lab of CI/CD

## Tomcat y observabilidad en Linux

El proyecto está en [`tomcat-observability/`](tomcat-observability/README.md). Incluye Tomcat 10.1 con JDK 17 sobre Alpine, Prometheus, Grafana, Alertmanager, Loki, Tempo y OpenTelemetry Collector, además de comprobaciones con Trivy y Checkov.

### Ejecutar desde la raíz del repositorio

Requisitos: Linux, Docker Engine arrancado, plugin Docker Compose v2 o posterior, Bash 4+, curl, jq y openssl. Reserva unos 4 GB de RAM y comprueba que tu usuario puede ejecutar Docker.

```bash
docker info
docker compose version
cd tomcat-observability
bash scripts/setup.sh
docker compose up -d --build
docker compose ps
```

Cuando los servicios estén listos:

```bash
bash scripts/smoke.sh
cat secrets/grafana_admin_password.txt
```

Abre Tomcat en http://localhost:8080 y Grafana en http://localhost:3000. En Grafana usa `admin` y la contraseña del archivo anterior. Prometheus está en http://localhost:9090 y Alertmanager en http://localhost:9093.

### Comprobar seguridad y detener

Desde `tomcat-observability/`:

```bash
# Checkov del Dockerfile y Trivy de todas las imágenes
bash scripts/security.sh --all-images

# Consultar logs
docker compose logs --tail 100 tomcat otel-collector

# Detener conservando los datos
docker compose down
```

Los informes de Trivy se guardan en `tomcat-observability/reports/`. El script devuelve un error si Checkov encuentra incumplimientos o Trivy detecta vulnerabilidades HIGH/CRITICAL.

Para acceder desde otro equipo, usa la IP del servidor: `http://IP_DEL_SERVIDOR:3000` (Grafana), `:8080` (Tomcat), `:9090` (Prometheus) y `:9093` (Alertmanager). Los puertos escuchan por defecto en todas las interfaces (`BIND_ADDRESS=0.0.0.0`). Puedes elegir una IP concreta en `tomcat-observability/.env`; aplica el cambio con `docker compose up -d` desde ese directorio. Si el firewall filtra estos puertos, permite el acceso desde tu IP o red de administración. Prometheus y Alertmanager no tienen autenticación configurada; limita su acceso a esa red.

Consulta la [guía completa del proyecto](tomcat-observability/README.md) para verificar métricas, logs y trazas, configurar notificaciones y gestionar los datos.

El dashboard **Tomcat observability** integra el [dashboard 8704](https://grafana.com/grafana/dashboards/8704-tomcat-dashboard/) adaptado a Grafana 12, con sus métricas JMX y un panel adicional de logs Loki. Para actualizar una instalación existente, desde `tomcat-observability/` ejecuta `docker compose up -d --build tomcat` y después `docker compose restart prometheus grafana`. Los volúmenes y el enlace al dashboard se conservan.
