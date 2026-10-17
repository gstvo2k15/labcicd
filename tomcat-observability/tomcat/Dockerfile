FROM alpine:3.24.2 AS download
ARG TOMCAT_VERSION=10.1.61
ARG OTEL_VERSION=2.26.1
ARG OTEL_SHA256=cc4af5966ab72109cacc962ba3b9f99b3e88caf064c3144a451bcfe0f4950f19
RUN apk add --no-cache ca-certificates curl tar \
    && mkdir -p /out/tomcat /out/agents \
    && curl -fsSL --retry 3 "https://archive.apache.org/dist/tomcat/tomcat-10/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz" -o /tmp/tomcat.tar.gz \
    && curl -fsSL --retry 3 "https://archive.apache.org/dist/tomcat/tomcat-10/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz.sha512" -o /tmp/tomcat.sha512 \
    && echo "$(cut -d ' ' -f 1 /tmp/tomcat.sha512)  /tmp/tomcat.tar.gz" | sha512sum -c - \
    && tar -xzf /tmp/tomcat.tar.gz --strip-components=1 -C /out/tomcat \
    && rm -rf /out/tomcat/webapps/* \
    && curl -fsSL --retry 3 "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_VERSION}/opentelemetry-javaagent.jar" -o /out/agents/opentelemetry-javaagent.jar \
    && echo "${OTEL_SHA256}  /out/agents/opentelemetry-javaagent.jar" | sha256sum -c -
# checkov:skip=CKV_DOCKER_2:Etapa de descarga; no ejecuta un servicio.
# checkov:skip=CKV_DOCKER_3:Etapa de descarga; apk requiere root. La imagen final usa UID 10001.

FROM alpine:3.24.2
LABEL org.opencontainers.image.title="Tomcat 10 / OpenJDK 17 observability lab"
RUN apk add --no-cache openjdk17-jdk ca-certificates \
    && addgroup -g 10001 tomcat \
    && adduser -D -H -u 10001 -G tomcat tomcat
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk \
    CATALINA_HOME=/opt/tomcat \
    PATH=/opt/tomcat/bin:/usr/lib/jvm/java-17-openjdk/bin:$PATH
COPY --from=download --chown=10001:10001 /out/ /opt/
COPY --chown=10001:10001 index.jsp /opt/tomcat/webapps/ROOT/index.jsp
WORKDIR /opt/tomcat
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
CMD ["catalina.sh", "run"]
