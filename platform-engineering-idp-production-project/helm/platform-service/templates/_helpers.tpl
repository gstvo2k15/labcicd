{{- define "platform-service.name" -}}{{ default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}{{- end -}}
{{- define "platform-service.fullname" -}}{{ default (include "platform-service.name" .) .Values.fullnameOverride }}{{- end -}}
