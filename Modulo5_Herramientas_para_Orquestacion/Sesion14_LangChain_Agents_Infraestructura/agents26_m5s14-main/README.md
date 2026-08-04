# agents26_m5s14
# Agents26 M5S14 - Agente Infra 🤖

> Solución completa de agentes de infraestructura con arquitectura cliente-servidor optimizada para deployment en **Azure Kubernetes Service (AKS)** con contenedores Docker.

---

## 📋 Contenido

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Local](#instalación-local)
- [Deployment en AKS](#deployment-en-aks)
- [Docker](#docker)
- [Configuración](#configuración)
- [Uso](#uso)
- [Contribuir](#contribuir)

---

## 📖 Descripción del Proyecto

**agents26_m5s14** es una plataforma de agentes de infraestructura que permite automatizar, monitorear y gestionar recursos en tiempo real. El proyecto sigue una arquitectura cliente-servidor modular, facilitando el escalado y deployment en entornos containerizados.

### Características Principales

✅ Arquitectura microservicios con cliente y servidor separados  
✅ Completamente containerizado con Docker  
✅ Deployment automático en AKS con Kubernetes  
✅ API REST para comunicación cliente-servidor  
✅ Escalado horizontal automático  
✅ Monitoreo y logging integrado  

---

## 🏗️ Arquitectura

### Diagrama de Arquitectura - Deployment en AKS

```
┌─────────────────────────────────────────────────────────────────┐
│                         AZURE CLOUD ENVIRONMENT                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           AZURE KUBERNETES SERVICE (AKS)                │   │
│  │                                                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │         CLIENT POD (Load Balanced)                │  │   │
│  │  │  ┌──────────────────────────────────────────────┐ │  │   │
│  │  │  │  Container: Client Application               │ │  │   │
│  │  │  │  • Image: agents26-client:latest             │ │  │   │
│  │  │  │  • Port: 5000                                │ │  │   │
│  │  │  │  • Replicas: 2-5 (Auto-scale)                │ │  │   │
│  │  │  │  • CPU Limit: 500m / Memory: 512Mi            │ │  │   │
│  │  │  └──────────────────────────────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                          ↕️ (Service)                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │        SERVER POD (Load Balanced)                 │  │   │
│  │  │  ┌──────────────────────────────────────────────┐ │  │   │
│  │  │  │  Container: Server Application               │ │  │   │
│  │  │  │  • Image: agents26-server:latest             │ │  │   │
│  │  │  │  • Port: 8000                                │ │  │   │
│  │  │  │  • Replicas: 2-5 (Auto-scale)                │ │  │   │
│  │  │  │  • CPU Limit: 1000m / Memory: 1Gi             │ │  │   │
│  │  │  │  • Volume Mount: /data (Persistent)          │ │  │   │
│  │  │  └──────────────────────────────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                           │   │
│  └────────────────────────────────────────────────────────┘  │   │
│                         ↕️                                     │   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    INGRESS CONTROLLER (Azure Application Gateway)        │   │
│  │    • External IP: xxx.xxx.xxx.xxx                        │   │
│  │    • Routes /client → Client Service (Port 5000)         │   │
│  │    • Routes /api → Server Service (Port 8000)            │   │
│  │    • SSL/TLS Termination                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              STORAGE & PERSISTENCE                        │   │
│  │  ┌──────────────────────────────────────────────────────┐│   │
│  │  │  • Persistent Volume Claims (PVC)                  ││   │
│  │  │  • Azure Disk Storage (Premium SSD)               ││   │
│  │  │  • ConfigMaps (Configuración)                     ││   │
│  │  │  • Secrets (API Keys, Passwords)                  ││   │
│  │  └──────────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓
    EXTERNAL USERS
```

### Componentes Principales

| Componente | Descripción | Tecnología |
|-----------|-------------|-----------|
| **Client** | Interfaz de usuario y aplicación cliente | Python/FastAPI |
| **Server** | API backend y lógica de negocios | Python/FastAPI |
| **Kubernetes** | Orquestación de contenedores | AKS (Azure) |
| **Storage** | Almacenamiento persistente | Azure Disk/Blob Storage |
| **Ingress** | Enrutamiento y balanceo de carga | Application Gateway |

---

## 📁 Estructura del Proyecto

```
agents26_m5s14/
│
├── client/                          # Aplicación Cliente
│   ├── app.py                       # Punto de entrada
│   ├── requirements.txt             # Dependencias Python
│   ├── Dockerfile                   # Imagen Docker para cliente
│   ├── docker-compose.yml           # Compose para desarrollo local
│   ├── src/
│   │   ├── api/
│   │   │   └── client.py           # Cliente HTTP
│   │   ├── models/
│   │   │   └── request.py          # Modelos de datos
│   │   └── utils/
│   │       └── config.py           # Configuración
│   └── kubernetes/
│       ├── deployment.yaml         # Deployment de K8s
│       ├── service.yaml            # Service de K8s
│       └── configmap.yaml          # ConfigMap
│
├── server/                          # Aplicación Servidor
│   ├── app.py                       # Punto de entrada
│   ├── requirements.txt             # Dependencias Python
│   ├── Dockerfile                   # Imagen Docker para servidor
│   ├── docker-compose.yml           # Compose para desarrollo local
│   ├── src/
│   │   ├── api/
│   │   │   └── router.py           # Rutas API
│   │   ├── models/
│   │   │   └── response.py         # Modelos de respuesta
│   │   ├── services/
│   │   │   └── agent_service.py    # Lógica de agentes
│   │   └── config/
│   │       └── settings.py         # Configuración
│   └── kubernetes/
│       ├── deployment.yaml         # Deployment de K8s
│       ├── service.yaml            # Service de K8s
│       ├── statefulset.yaml        # StatefulSet para persistencia
│       ├── configmap.yaml          # ConfigMap
│       ├── pvc.yaml                # Persistent Volume Claim
│       └── hpa.yaml                # Horizontal Pod Autoscaler
│
├── kubernetes/                      # Configuración Kubernetes global
│   ├── ingress.yaml               # Ingress Controller
│   ├── namespace.yaml             # Namespace
│   ├── secrets.yaml               # Secrets (base64)
│   └── monitoring/
│       ├── prometheus.yaml        # Monitoreo
│       └── grafana.yaml           # Dashboards
│
├── docker-compose.yml               # Compose para todo el proyecto
├── .dockerignore                    # Archivos a ignorar en Docker
├── .gitignore                       # Archivos a ignorar en Git
├── requirements.txt                 # Dependencias globales
├── README.md                        # Este archivo
└── scripts/
    ├── build.sh                     # Script para build de imágenes
    ├── deploy.sh                    # Script para deploy en AKS
    ├── setup-aks.sh                 # Script para crear cluster AKS
    └── cleanup.sh                   # Script para limpiar recursos
```

---

## 🔧 Requisitos Previos

### Local Development
- **Python 3.9+**
- **Docker Desktop** (o Docker Engine)
- **Docker Compose 2.0+**
- **Git**

### Deployment en Azure (AKS)
- **Azure CLI** (`az` command)
- **kubectl** (1.24+)
- **Helm** (3.0+)
- **Cuenta de Azure** con permisos para crear recursos
- **Container Registry** (ACR - Azure Container Registry)

### Instalación de Requisitos

```bash
# macOS (Homebrew)
brew install python docker docker-compose azure-cli kubectl helm

# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 docker.io docker-compose azure-cli kubectl helm
sudo usermod -aG docker $USER

# Windows (Chocolatey)
choco install python docker-cli azure-cli kubectl helm
```

---

## 🚀 Instalación Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/alzamoralabs/agents26_m5s14.git
cd agents26_m5s14
```

### 2. Opción A: Docker Compose (Recomendado)

```bash
# Construir imágenes
docker-compose build

# Iniciar los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

**Acceso:**
- Cliente: http://localhost:5000
- Servidor: http://localhost:8000
- Health Check: http://localhost:8000/health

### 3. Opción B: Instalación Manual

```bash
# Client
cd client
pip install -r requirements.txt
python app.py

# En otra terminal - Server
cd server
pip install -r requirements.txt
python app.py
```

---

## ☸️ Deployment en AKS

### 1. Preparar Azure

```bash
# Loguear en Azure
az login

# Crear grupo de recursos
az group create \
  --name agents26-rg \
  --location eastus

# Crear Azure Container Registry
az acr create \
  --resource-group agents26-rg \
  --name agents26acr \
  --sku Basic
```

### 2. Crear Cluster AKS

```bash
az aks create \
  --resource-group agents26-rg \
  --name agents26-aks \
  --node-count 2 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --enable-managed-identity \
  --network-plugin azure \
  --network-policy azure \
  --docker-bridge-address 172.17.0.1/16 \
  --service-cidr 10.0.0.0/16 \
  --dns-service-ip 10.0.0.10
```

### 3. Obtener Credenciales

```bash
az aks get-credentials \
  --resource-group agents26-rg \
  --name agents26-aks

# Verificar conexión
kubectl cluster-info
kubectl get nodes
```

### 4. Construir y Pushear Imágenes

```bash
# Login en ACR
az acr login --name agents26acr

# Construir y pushear Client
docker build -t agents26acr.azurecr.io/client:latest ./client
docker push agents26acr.azurecr.io/client:latest

# Construir y pushear Server
docker build -t agents26acr.azurecr.io/server:latest ./server
docker push agents26acr.azurecr.io/server:latest

# Verificar imágenes en ACR
az acr repository list --name agents26acr
```

### 5. Configurar AKS para usar ACR

```bash
az aks update \
  --name agents26-aks \
  --resource-group agents26-rg \
  --attach-acr agents26acr
```

### 6. Crear Namespace

```bash
kubectl create namespace agents26
kubectl config set-context --current --namespace=agents26
```

### 7. Crear Secrets (Variables Sensibles)

```bash
# Crear secret con credenciales
kubectl create secret generic app-secrets \
  --from-literal=API_KEY='your-api-key' \
  --from-literal=DB_PASSWORD='your-password' \
  -n agents26

# O usar el archivo secrets.yaml (encoded)
kubectl apply -f kubernetes/secrets.yaml
```

### 8. Desplegar Aplicaciones

```bash
# Desplegar Namespace y configuración
kubectl apply -f kubernetes/namespace.yaml

# Desplegar Server
kubectl apply -f server/kubernetes/

# Desplegar Client
kubectl apply -f client/kubernetes/

# Desplegar Ingress
kubectl apply -f kubernetes/ingress.yaml

# Verificar deployments
kubectl get deployments -n agents26
kubectl get pods -n agents26
kubectl get svc -n agents26
```

### 9. Obtener Punto de Acceso Externo

```bash
# Esperar a que se asigne IP externa
kubectl get ingress -n agents26 --watch

# O ver detalles del ingress
kubectl describe ingress -n agents26
```

### 10. Monitoreo y Logs

```bash
# Ver logs en tiempo real
kubectl logs -f deployment/server -n agents26
kubectl logs -f deployment/client -n agents26

# Ver descripción del pod
kubectl describe pod <pod-name> -n agents26

# Acceder a un pod (terminal interactivo)
kubectl exec -it <pod-name> -n agents26 -- /bin/bash
```

---

## 🐳 Docker

### Archivos Dockerfile

#### Client Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Server Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/data"]
EXPOSE 8000

CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  server:
    build:
      context: ./server
      dockerfile: Dockerfile
    container_name: agents26-server
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./server:/app
      - server-data:/data
    networks:
      - agents26-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    container_name: agents26-client
    ports:
      - "5000:5000"
    environment:
      - SERVER_URL=http://server:8000
      - DEBUG=False
    volumes:
      - ./client:/app
    depends_on:
      server:
        condition: service_healthy
    networks:
      - agents26-network

volumes:
  server-data:

networks:
  agents26-network:
    driver: bridge
```

---

## ⚙️ Configuración

### Variables de Entorno

#### Client (.env)
```env
SERVER_URL=http://localhost:8000
CLIENT_PORT=5000
LOG_LEVEL=INFO
DEBUG=False
```

#### Server (.env)
```env
SERVER_PORT=8000
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=your-api-key
LOG_LEVEL=INFO
DEBUG=False
WORKERS=4
```

#### AKS/Kubernetes
```yaml
# Usando ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: agents26
data:
  SERVER_URL: "http://server:8000"
  LOG_LEVEL: "INFO"
  
---
# Usando Secrets (base64)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: agents26
type: Opaque
data:
  API_KEY: eW91ci1hcGkta2V5  # base64 encoded
  DB_PASSWORD: eW91ci1wYXNzd29yZA==  # base64 encoded
```

---

## 📊 Monitoreo en AKS

### Habilitar Container Insights (Azure Monitor)

```bash
az aks enable-addons \
  --resource-group agents26-rg \
  --name agents26-aks \
  --addons monitoring
```

### Dashboard Prometheus/Grafana

```bash
# Instalar Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Port Forward para acceder a Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Acceder a http://localhost:3000
# Usuario: admin, Contraseña: prom-operator
```

---

## 📈 Escalado Automático (HPA)

```yaml
# server/kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: server-hpa
  namespace: agents26
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 🔄 CI/CD con GitHub Actions

Crear archivo `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AKS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to ACR
      uses: azure/docker-login@v1
      with:
        login-server: agents26acr.azurecr.io
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - name: Build and push images
      run: |
        docker build -t agents26acr.azurecr.io/client:${{ github.sha }} ./client
        docker push agents26acr.azurecr.io/client:${{ github.sha }}
        
        docker build -t agents26acr.azurecr.io/server:${{ github.sha }} ./server
        docker push agents26acr.azurecr.io/server:${{ github.sha }}
    
    - name: Set AKS context
      uses: azure/aks-set-context@v3
      with:
        resource-group: agents26-rg
        cluster-name: agents26-aks
        credentials: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to AKS
      run: |
        kubectl set image deployment/server \
          server=agents26acr.azurecr.io/server:${{ github.sha }} \
          -n agents26
        kubectl set image deployment/client \
          client=agents26acr.azurecr.io/client:${{ github.sha }} \
          -n agents26
```

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Coverage
pytest --cov=src tests/

# Load testing con locust
locust -f tests/load_test.py -u 100 -r 10
```

---

## 📝 API Endpoints

### Server API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/status` | Estado del sistema |
| `POST` | `/api/tasks` | Crear tarea |
| `GET` | `/api/tasks/{id}` | Obtener tarea |
| `PUT` | `/api/tasks/{id}` | Actualizar tarea |
| `DELETE` | `/api/tasks/{id}` | Eliminar tarea |

---

## 🛠️ Troubleshooting

### El pod no inicia

```bash
# Ver logs
kubectl logs <pod-name> -n agents26

# Ver eventos
kubectl describe pod <pod-name> -n agents26

# Ver recursos disponibles
kubectl top nodes
kubectl top pods -n agents26
```

### Problemas de conectividad

```bash
# Verificar servicio
kubectl get svc -n agents26

# Hacer port-forward para debug
kubectl port-forward svc/server 8000:8000 -n agents26
curl http://localhost:8000/health
```

### Limpiar recursos

```bash
# Eliminar deployment
kubectl delete deployment server -n agents26

# Eliminar todo el namespace
kubectl delete namespace agents26

# Eliminar cluster AKS
az aks delete \
  --resource-group agents26-rg \
  --name agents26-aks
```

---

## 📚 Documentación Adicional

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Azure Kubernetes Service](https://docs.microsoft.com/en-us/azure/aks/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👥 Autores

- **Alzamora Labs** - [GitHub](https://github.com/alzamoralabs)

---

## 📞 Soporte

Para reportar bugs o solicitar features, abre un [issue](https://github.com/alzamoralabs/agents26_m5s14/issues).

Para preguntas generales, contacta a través de [Discussions](https://github.com/alzamoralabs/agents26_m5s14/discussions).

---

**Última actualización:** Julio 2026 | Version: 1.0.0