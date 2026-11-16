{{- define "portal.name" -}}
{{- .Release.Name | trunc 40 | trimSuffix "-" -}}
{{- end -}}

{{- define "portal.labels" -}}
app.kubernetes.io/name: change-request-portal
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "portal.selector" -}}
app.kubernetes.io/name: change-request-portal
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "portal.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}
{{- end -}}

{{- define "portal.secretName" -}}
{{- .Values.secrets.existingSecret | default (include "portal.name" .) -}}
{{- end -}}

{{- define "portal.dbHost" -}}
{{- if .Values.postgresql.enabled -}}
{{ include "portal.name" . }}-db
{{- else -}}
{{ required "Set externalDatabase.host, or postgresql.enabled=true" .Values.externalDatabase.host }}
{{- end -}}
{{- end -}}

{{- define "portal.dbPort" -}}
{{- if .Values.postgresql.enabled -}}5432{{- else -}}{{ .Values.externalDatabase.port }}{{- end -}}
{{- end -}}

{{/* Environment shared by the web pods and the migration Job. */}}
{{- define "portal.env" -}}
envFrom:
  - configMapRef:
      name: {{ include "portal.name" . }}
env:
  - name: DJANGO_SECRET_KEY
    valueFrom: {secretKeyRef: {name: {{ include "portal.secretName" . }}, key: django-secret-key}}
  - name: POSTGRES_PASSWORD
    valueFrom: {secretKeyRef: {name: {{ include "portal.secretName" . }}, key: postgres-password}}
  {{- if .Values.oidc.clientId }}
  - name: OIDC_RP_CLIENT_SECRET
    valueFrom: {secretKeyRef: {name: {{ include "portal.secretName" . }}, key: oidc-client-secret}}
  {{- end }}
  {{- if .Values.email.user }}
  - name: EMAIL_HOST_PASSWORD
    valueFrom: {secretKeyRef: {name: {{ include "portal.secretName" . }}, key: email-password}}
  {{- end }}
{{- end -}}

{{/* The portal container never needs root, extra privileges or a writable disk. */}}
{{- define "portal.containerSecurity" -}}
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: {drop: [ALL]}
{{- end -}}

{{- define "portal.scheduling" -}}
{{- with .Values.imagePullSecrets }}
imagePullSecrets: {{ toYaml . | nindent 2 }}
{{- end }}
{{- with .Values.nodeSelector }}
nodeSelector: {{ toYaml . | nindent 2 }}
{{- end }}
{{- with .Values.tolerations }}
tolerations: {{ toYaml . | nindent 2 }}
{{- end }}
{{- end -}}
