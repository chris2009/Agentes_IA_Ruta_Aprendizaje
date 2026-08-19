# Physical AI Agent para Monitoreo Inteligente de Gatos
## Tapo C220 + RTSP + YOLO + LangChain/LangGraph + MCP

**Documento técnico de diseño, compra e implementación**  
**Fecha de verificación de precios y compatibilidad:** 13 de agosto de 2026

---

## 1. Resumen ejecutivo

El proyecto es **técnicamente viable** y encaja muy bien como una prueba académica de **Physical AI Agent Interfaces** porque integra:

- un **sensor físico real**: cámara IP;
- percepción del entorno mediante **visión computacional**;
- detección de objetos con **YOLO**;
- identificación de dos gatos visualmente diferentes;
- memoria temporal del estado de cada gato;
- generación de eventos;
- razonamiento y coordinación mediante **LangChain/LangGraph**;
- acceso a dispositivos Tapo mediante **MCP**;
- generación de alertas cuando cambia el estado del entorno.

El caso de uso propuesto es:

> **Construir un agente físico capaz de monitorear dos gatos en un entorno doméstico, detectar cuándo aparecen o desaparecen, identificar cuál de los dos está presente y generar alertas según reglas temporales y contextuales.**

El proyecto se recomienda desarrollar en dos canales paralelos:

1. **RTSP → OpenCV/YOLO** para analizar el video continuamente.
2. **Tapo MCP** para integrar la cámara y otros dispositivos Tapo como herramientas utilizables por el agente.

> **Punto crítico:** el MCP de Tapo actualmente expone snapshots de la cámara, pero no entrega el video RTSP continuo como una herramienta MCP. Por ello, el procesamiento en tiempo real debe hacerse directamente sobre RTSP.

---

# 2. Idea del proyecto

## Nombre sugerido

### Opción académica
**Physical AI Agent para monitoreo inteligente de mascotas mediante visión computacional, cámara IoT y Model Context Protocol**

### Opción corta
**CatWatch AI Agent**

### Opción descriptiva
**Agente inteligente para detección, identificación y monitoreo de gatos en un entorno doméstico**

---

# 3. Objetivo general

Diseñar e implementar un agente de inteligencia artificial con interacción física capaz de monitorear en tiempo real la presencia de dos gatos mediante una cámara IoT, visión computacional y modelos de detección de objetos, generando alertas automáticas según cambios observados en el entorno.

---

# 4. Objetivos específicos

1. Capturar el video en tiempo real de una cámara Tapo mediante RTSP.
2. Detectar gatos en el video utilizando YOLO.
3. Diferenciar visualmente los dos gatos monitoreados.
4. Registrar el estado temporal de presencia de cada gato.
5. Generar eventos cuando:
   - no haya gatos presentes;
   - aparezca solamente el gato naranja;
   - aparezca solamente el gato negro;
   - estén ambos presentes;
   - alguno desaparezca del área monitoreada;
   - alguno permanezca ausente durante un tiempo definido.
6. Integrar el sistema de percepción con un agente LangChain/LangGraph.
7. Integrar el ecosistema Tapo mediante MCP.
8. Generar alertas o acciones físicas como respuesta a eventos observados.

---

# 5. Estados principales del sistema

El sistema puede representar el entorno mediante cuatro estados simples:

| Estado | Gato naranja | Gato negro | Interpretación |
|---|---:|---:|---|
| `NONE` | No | No | Ningún gato está visible |
| `ORANGE_ONLY` | Sí | No | Solo está el gato naranja |
| `BLACK_ONLY` | No | Sí | Solo está el gato negro |
| `BOTH` | Sí | Sí | Ambos están presentes |

Ejemplo:

```text
21:02  Gato naranja detectado
21:04  Gato negro detectado
21:04  Estado = BOTH

21:17  Gato naranja deja de ser visible
21:17  Estado = BLACK_ONLY

21:32  Gato negro deja de ser visible
21:32  Estado = NONE

21:40  Gato naranja reaparece
21:40  Estado = ORANGE_ONLY
```

---

# 6. Arquitectura propuesta

```mermaid
flowchart TD
    A[Entorno físico: gatos] --> B[Tapo C220]
    B -->|RTSP| C[OpenCV]
    C --> D[YOLO]
    D --> E[Tracking]
    E --> F[Identificación: naranja / negro]
    F --> G[Motor de estados]
    G --> H[Memoria temporal]
    H --> I[Agente LangChain / LangGraph]

    B -->|MCP / snapshot / estado| J[Tapo MCP]
    J --> I

    I --> K[Alertas]
    I --> L[Registro histórico]
    I --> M[Resumen diario]
    I --> N[Actuador opcional]
```

---

# 7. Flujo lógico recomendado

```text
CÁMARA TAPO
     ↓
VIDEO RTSP
     ↓
OpenCV
     ↓
YOLO
     ↓
DETECCIÓN DE "CAT"
     ↓
TRACKING
     ↓
IDENTIFICACIÓN
  ┌───────────────┐
  │ gato naranja  │
  │ gato negro    │
  └───────────────┘
     ↓
MOTOR DE ESTADOS
     ↓
MEMORIA TEMPORAL
     ↓
AGENTE
     ↓
DECISIÓN
     ↓
ALERTA / ACCIÓN
```

---

# 8. ¿Por qué YOLO?

YOLO funcionará como la capa de **percepción visual**.

No es necesario enviar todos los frames a un LLM.

La arquitectura correcta es:

```text
30 FPS de cámara
      ↓
YOLO procesa video
      ↓
genera detecciones estructuradas
      ↓
solo los eventos relevantes llegan al agente
```

Ejemplo de información que podría producir la capa de visión:

```json
{
  "timestamp": "2026-08-13T21:17:02",
  "orange_cat": true,
  "black_cat": false,
  "cats_detected": 1,
  "state": "ORANGE_ONLY"
}
```

El agente recibe información estructurada y no el video completo.

---

# 9. Identificación de los dos gatos

El proyecto tiene una ventaja importante: los dos animales son visualmente muy distintos.

- **Gato 1:** pelaje naranja.
- **Gato 2:** pelaje negro.

Esto reduce considerablemente la dificultad.

## Estrategia A — MVP recomendado

```text
YOLO detecta "cat"
       ↓
se recorta bounding box
       ↓
clasificación visual
       ↓
naranja / negro
```

Se puede comenzar usando características cromáticas simples en HSV.

### Ventajas

- rápida de implementar;
- requiere poco entrenamiento;
- suficiente para la primera demostración.

### Limitación

Cuando la cámara entra en **visión nocturna infrarroja**, la imagen puede perder color y verse en escala de grises.

---

## Estrategia B — Recomendada para versión final

Entrenar un pequeño clasificador de imágenes con dos clases:

```text
class_0 = gato_naranja
class_1 = gato_negro
```

Dataset sugerido:

- 300–500 imágenes del gato naranja;
- 300–500 imágenes del gato negro;
- diferentes posiciones;
- diferentes distancias;
- diferentes horas del día;
- diferentes niveles de iluminación;
- imágenes nocturnas;
- gatos parcialmente ocultos.

---

## Estrategia C — YOLO personalizado

Entrenar directamente un modelo YOLO con:

```text
gato_naranja
gato_negro
```

Esto permite que el detector entregue directamente:

```text
gato_naranja  0.96
gato_negro    0.93
```

Es la opción más elegante para una demostración académica.

---

# 10. Tracking

YOLO detecta objetos, pero para saber que un gato continúa siendo el mismo mientras se mueve conviene añadir tracking.

Opciones:

- ByteTrack;
- BoT-SORT;
- DeepSORT.

Flujo:

```text
YOLO
  ↓
detección
  ↓
tracker
  ↓
track_id
  ↓
identidad del gato
```

Ejemplo:

```text
track_id = 7
identity = orange_cat
```

---

# 11. Evitar falsas alertas

Nunca se debe asumir que un gato desapareció porque YOLO dejó de detectarlo en un solo frame.

Ejemplo:

```text
Frame 1 → gato negro detectado
Frame 2 → gato negro detectado
Frame 3 → gato queda detrás de una silla
Frame 4 → no detectado
Frame 5 → gato negro detectado
```

Sin lógica temporal se produciría una falsa alerta.

## Regla recomendada

Definir:

```text
PRESENCE_TIMEOUT = 5 segundos
ABSENCE_ALERT = 30 segundos
ALERT_COOLDOWN = 60 segundos
```

Ejemplo:

```python
if current_time - last_seen_black < 5:
    black_present = True
else:
    black_present = False
```

Una alerta de ausencia solamente se genera después de un tiempo razonable.

---

# 12. Cámara recomendada

# TP-Link Tapo C220

## Veredicto

**Es la cámara recomendada para el proyecto por relación precio / prestaciones / compatibilidad.**

---

## Características relevantes

| Característica | Tapo C220 |
|---|---|
| Resolución | 2K QHD, 4 MP |
| Resolución máxima | 2560 × 1440 |
| FPS | 15 / 20 / 25 / 30 fps |
| Compresión | H.264 |
| Movimiento horizontal | 360° |
| Movimiento vertical | 114° |
| RTSP | Sí |
| ONVIF | Sí |
| Wi-Fi | 2.4 GHz |
| Audio bidireccional | Sí |
| microSD | Hasta 512 GB |
| Visión nocturna | IR, hasta aprox. 9 m |
| Detección de mascotas | Sí |
| Detección de personas | Sí |
| Detección de vehículos | Sí |
| Detección de maullidos | Disponible como función de IA |
| Integración Alexa / Google | Sí |

Fuente oficial:
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c220/

---

# 13. Compatibilidad con RTSP

TP-Link confirma oficialmente que la Tapo C220 soporta RTSP.

Las cámaras Tapo utilizan:

```text
RTSP: 554
ONVIF: 2020
```

Streams estándar:

```text
Alta calidad:
rtsp://IP_CAMARA:554/stream1

Calidad estándar:
rtsp://IP_CAMARA:554/stream2
```

Cuando se incluyen credenciales:

```text
rtsp://usuario:password@IP_CAMARA:554/stream1
```

Fuente oficial:
https://www.tp-link.com/pe/support/faq/4465/

Guía oficial:
https://www.tp-link.com/es/support/faq/2680/

---

# 14. Creación de la cuenta de cámara Tapo

La cuenta de cámara **no es la misma cuenta Tapo Cloud**.

En la aplicación Tapo:

```text
Tapo App
   ↓
Cámara
   ↓
Vista en directo
   ↓
Configuración
   ↓
Configuración avanzada
   ↓
Cuenta de cámara
```

Crear:

```text
CAMERA_USERNAME
CAMERA_PASSWORD
```

Usar una contraseña exclusiva para esta cuenta.

No publicar las credenciales en GitHub.

---

# 15. Prueba inicial del RTSP

Antes de programar YOLO:

1. Instalar VLC.
2. Abrir:
   - Medio
   - Abrir ubicación de red.
3. Introducir:

```text
rtsp://usuario:password@192.168.X.X:554/stream1
```

Si aparece video en vivo, la parte más importante de la integración está funcionando.

---

# 16. Cámaras comparadas

## Tapo C210

| Característica | Valor |
|---|---|
| Resolución | 3 MP |
| Máxima resolución | 2304 × 1296 |
| FPS | 15 fps |
| Panorámica | 360° |
| RTSP | Sí |
| ONVIF | Sí |
| Visión nocturna | hasta 9 m |
| Compatibilidad con proyecto Tapo/MCP | Sí |

Precio encontrado en Perú:

- **Memory Kings:** aprox. S/ 92.50
- **Compupal Perú:** aprox. S/ 96.15
- **Arteus:** aprox. S/ 98.00

Fuente oficial:
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c210/

### Evaluación

Buena opción económica, pero por una diferencia pequeña de precio la C220 ofrece 4 MP y hasta 30 fps, por lo que resulta más apropiada para visión computacional.

---

# 17. Tapo C220 — recomendada

| Característica | Valor |
|---|---|
| Resolución | 4 MP |
| Máxima resolución | 2560 × 1440 |
| FPS | hasta 30 fps |
| Panorámica | 360° |
| Vertical | 114° |
| RTSP | Sí |
| ONVIF | Sí |
| H.264 | Sí |
| MCP compatible | Sí |
| Relación costo / proyecto | Excelente |

### Precio encontrado

#### Compupal Perú

**Precio observado:** S/ 95.15  
**Stock mostrado:** 9 unidades  
**Disponibilidad:** inmediata

Producto:
https://www.compupalperu.com/producto/camara_ip_tplink_tapo_c220

#### Arteus Perú

**Precio observado:** S/ 106.00

Producto:
https://arteus.pe/products/tp-link-tapo-c220-camara-de-seguridad-wifi-4mp-2k-360%C2%BA-pt

#### Mercado Libre Perú

**Precio observado:** aproximadamente S/ 116.76 para una publicación encontrada durante la revisión.

Producto:
https://www.mercadolibre.com.pe/tp-link-tapo-c220-camara-wifi-4mp-2k-360-interior-con-vision-nocturna-y-alarma/p/MPE38191961

> Los precios y el stock pueden cambiar en cualquier momento. Verificar antes de pagar.

---

# 18. Tienda recomendada

## Compupal Perú

Por precio y stock observado durante la revisión:

```text
Tapo C220
Precio: S/ 95.15
Stock mostrado: 9 unidades
Disponibilidad: inmediata
```

Sitio:
https://www.compupalperu.com/producto/camara_ip_tplink_tapo_c220

La web indica sedes en:

- Cyberplaza;
- Compuplaza;
- Comas.

## Recomendación de compra

Antes de pagar:

1. confirmar que el modelo sea exactamente **Tapo C220**;
2. confirmar versión de hardware;
3. solicitar comprobante;
4. verificar garantía;
5. confirmar stock;
6. confirmar costo de delivery.

---

# 19. Tapo C225

La C225 es una opción superior para escenarios con baja iluminación.

| Característica | Tapo C225 |
|---|---|
| Resolución | 2K QHD 4 MP |
| Máxima resolución | 2560 × 1440 |
| FPS | hasta 30 fps |
| Panorámica | 360° |
| Sensor Starlight | Sí |
| Visión nocturna en color | Sí, dependiendo de condiciones |
| IR invisible | Sí |
| RTSP | Sí |
| ONVIF | Sí |
| MCP compatible | Sí |
| Seguimiento rápido | hasta 120°/s |
| HomeKit | Sí |

Fuente oficial:
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c225/

### Precio observado

#### Memory Kings

```text
aprox. S/ 158.00
stock mostrado: 10 o más unidades
```

https://www.memorykings.pe/producto/347086/camara-cloud-wifi-tp-link-tapo-c225-2k-qhd-p-t-msd

#### Arteus

```text
aprox. S/ 168.00
```

https://arteus.pe/products/tp-link-tapo-c225-camara-de-seguridad-inalambrica-2k-qhd-deteccion-mascotas-personas-y-ruidos-abnormal-areas-de-deteccion

---

# 20. C220 vs C225 para este proyecto

| Factor | C220 | C225 |
|---|---:|---:|
| Precio | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 4 MP | Sí | Sí |
| 30 fps | Sí | Sí |
| RTSP | Sí | Sí |
| ONVIF | Sí | Sí |
| MCP soportado | Sí | Sí |
| Sensor Starlight | No equivalente al C225 | Sí |
| Baja luz | Buena | Mejor |
| Proyecto diurno | Excelente | Excelente |
| Proyecto nocturno | Buena | Mejor |
| Mejor relación costo/beneficio | **Sí** | No |

## Decisión

### Comprar C220 si:

- el proyecto es académico;
- se realizará principalmente con iluminación normal;
- se busca gastar lo mínimo;
- se quiere experimentar con YOLO y RTSP.

### Comprar C225 si:

- la identificación nocturna es prioritaria;
- se quiere mayor rendimiento en baja iluminación;
- el presupuesto adicional no es problema.

### Recomendación final

**Tapo C220.**

---

# 21. MCP seleccionado

Proyecto:

**mihai-dinculescu/tapo**

Repositorio:
https://github.com/mihai-dinculescu/tapo

Directorio MCP:
https://github.com/mihai-dinculescu/tapo/tree/main/tapo-mcp

Directorio consultado originalmente:
https://mcpservers.org/servers/mihai-dinculescu/tapo

> Para implementación se recomienda usar GitHub como fuente principal, porque es el repositorio del proyecto y contiene el código y documentación actualizados.

---

# 22. Cámaras probadas por el proyecto Tapo

El repositorio declara compatibilidad con:

```text
C210
C220
C225
C325WB
C520WS
TC40
TC70
```

Para cámaras, la biblioteca Tapo dispone de funciones como:

```text
get_rtsp_stream_url
get_snapshot
get_presets
goto_preset
save_preset
delete_preset
pan_tilt
get_device_info
```

Fuente:
https://github.com/mihai-dinculescu/tapo/blob/main/SUPPORTED_DEVICES.md

---

# 23. Qué expone actualmente el MCP

El servidor MCP actual expone principalmente:

```text
list_devices
check_device
get_device_state
control_device
take_snapshot
```

`take_snapshot` captura una imagen JPEG de aproximadamente:

```text
640 × 360
```

El MCP funciona mediante **Streamable HTTP**.

Fuente:
https://github.com/mihai-dinculescu/tapo/tree/main/tapo-mcp

---

# 24. Limitación importante del MCP

El MCP actual **NO expone el stream RTSP continuo como una tool**.

Por tanto:

```text
MCP
 ↓
snapshot
```

pero no:

```text
MCP
 ↓
30 FPS
 ↓
YOLO
```

Para detección continua:

```text
Tapo C220
   ↓
RTSP
   ↓
OpenCV
   ↓
YOLO
```

El MCP complementa al sistema para:

- descubrimiento;
- lectura de estado;
- snapshots bajo demanda;
- acceso agentic a dispositivos Tapo.

---

# 25. Otra precisión importante: Pan/Tilt

La **biblioteca Tapo** soporta `pan_tilt` para cámaras compatibles.

Sin embargo, el MCP actual listado en su README no publica `pan_tilt` como una tool específica.

Por ello:

### Si se necesita mover la cámara desde el agente

Usar una de estas alternativas:

1. biblioteca Tapo Python/Rust directamente;
2. ONVIF;
3. ampliar el MCP añadiendo una tool `pan_tilt`.

Esto podría convertirse incluso en una mejora adicional del proyecto.

---

# 26. Configuración del Tapo MCP

Variables utilizadas por el MCP:

```text
TAPO_MCP_USERNAME
TAPO_MCP_PASSWORD
TAPO_MCP_CAMERA_USERNAME
TAPO_MCP_CAMERA_PASSWORD
TAPO_MCP_DISCOVERY_TARGET
TAPO_MCP_HTTP_ADDR
TAPO_MCP_API_KEY
TAPO_MCP_ALLOWED_HOSTS
```

Ejemplo conceptual:

```bash
TAPO_MCP_USERNAME="correo_tapo"
TAPO_MCP_PASSWORD="password_tapo"

TAPO_MCP_CAMERA_USERNAME="camera_user"
TAPO_MCP_CAMERA_PASSWORD="camera_password"

TAPO_MCP_DISCOVERY_TARGET="192.168.1.255"

TAPO_MCP_HTTP_ADDR="127.0.0.1:3000"
```

No subir estas credenciales al repositorio.

---

# 27. Endpoint del MCP

En el código actual, el servicio Streamable HTTP se publica en la ruta raíz:

```text
/
```

Por defecto:

```text
http://127.0.0.1:3000/
```

Fuente:
https://github.com/mihai-dinculescu/tapo/blob/main/tapo-mcp/src/lib.rs

---

# 28. Integración con LangChain

Instalar:

```bash
pip install langchain
pip install langgraph
pip install langchain-mcp-adapters
```

LangChain permite cargar herramientas MCP mediante:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
```

Ejemplo conceptual:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "tapo": {
            "transport": "http",
            "url": "http://127.0.0.1:3000/"
        }
    }
)

tools = await client.get_tools()
```

Si se activa `TAPO_MCP_API_KEY`:

```python
client = MultiServerMCPClient(
    {
        "tapo": {
            "transport": "http",
            "url": "http://127.0.0.1:3000/",
            "headers": {
                "Authorization": "Bearer TU_API_KEY"
            }
        }
    }
)
```

Documentación oficial LangChain:
https://docs.langchain.com/oss/python/langchain/mcp

Repositorio:
https://github.com/langchain-ai/langchain-mcp-adapters

---

# 29. Advertencia para Docker en Windows y macOS

El README actual de Tapo MCP señala que el descubrimiento de dispositivos depende de broadcast UDP.

Con Docker:

```text
--network host
```

es necesario para que el contenedor llegue correctamente a los dispositivos mediante descubrimiento.

El proyecto advierte que Docker Desktop en:

```text
Windows
macOS
```

no soporta este comportamiento del mismo modo que Linux y el descubrimiento de dispositivos puede no funcionar.

## Recomendación

Para la prueba MCP:

### Mejor opción

Ejecutar el MCP en:

- Linux nativo;
- Raspberry Pi;
- mini PC Linux;
- una máquina Linux en la misma LAN con red adecuada.

### Alternativa

Compilar/ejecutar el proyecto nativamente en el sistema operativo objetivo.

> No asumir que ejecutar Docker Desktop con `-p 3000:3000` permitirá descubrimiento automático.

---

# 30. Seguridad del MCP

Si el MCP escucha solamente en:

```text
127.0.0.1
```

se mantiene local.

Si se expone hacia la LAN:

```text
0.0.0.0:3000
```

el proyecto exige utilizar una API key.

Ejemplo:

```text
TAPO_MCP_API_KEY=<clave_segura>
```

También se puede controlar:

```text
TAPO_MCP_ALLOWED_HOSTS
```

Nunca publicar un MCP de dispositivos físicos directamente hacia Internet sin controles de autenticación.

---

# 31. Seguridad del RTSP

TP-Link recomienda utilizar RTSP/ONVIF en redes locales confiables.

No se recomienda abrir directamente el puerto RTSP:

```text
554
```

a Internet.

Para acceso remoto se recomienda:

```text
VPN
```

en lugar de mantener un port-forwarding público permanente.

Fuente oficial:
https://www.tp-link.com/pe/support/faq/4465/

---

# 32. Estructura de software recomendada

```text
catwatch-agent/
│
├── app/
│   ├── camera.py
│   ├── detector.py
│   ├── tracker.py
│   ├── identity.py
│   ├── state_machine.py
│   ├── memory.py
│   ├── alerts.py
│   ├── agent.py
│   └── main.py
│
├── config/
│   └── settings.py
│
├── data/
│   ├── events/
│   ├── snapshots/
│   └── dataset/
│
├── models/
│   └── cat_identity.pt
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 33. Dependencias sugeridas

```bash
pip install ultralytics
pip install opencv-python
pip install numpy
pip install python-dotenv
pip install langchain
pip install langgraph
pip install langchain-mcp-adapters
```

Opcionales:

```bash
pip install pillow
pip install requests
```

---

# 34. Archivo `.env`

Ejemplo:

```env
TAPO_CAMERA_IP=192.168.1.50
TAPO_CAMERA_USER=camera_user
TAPO_CAMERA_PASSWORD=CAMBIAR

RTSP_STREAM=rtsp://camera_user:CAMBIAR@192.168.1.50:554/stream1

MCP_URL=http://127.0.0.1:3000/
MCP_API_KEY=CAMBIAR
```

Agregar `.env` a:

```text
.gitignore
```

---

# 35. Prueba básica con OpenCV

```python
import cv2

RTSP_URL = "rtsp://usuario:password@192.168.1.50:554/stream1"

cap = cv2.VideoCapture(RTSP_URL)

while True:
    ret, frame = cap.read()

    if not ret:
        print("No se pudo leer el stream")
        break

    cv2.imshow("Tapo Live", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

Objetivo:

```text
Tapo → RTSP → OpenCV
```

Antes de añadir IA.

---

# 36. Prueba básica con YOLO

Ejemplo:

```python
import cv2
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(
    "rtsp://usuario:password@192.168.1.50:554/stream1"
)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    annotated = results[0].plot()

    cv2.imshow("CatWatch", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

Primer objetivo:

```text
detectar class = cat
```

---

# 37. Pipeline de identificación

```python
for detection in detections:

    if detection.class_name == "cat":

        crop = frame[y1:y2, x1:x2]

        identity = classify_cat(crop)

        if identity == "orange":
            last_seen_orange = now

        elif identity == "black":
            last_seen_black = now
```

---

# 38. Máquina de estados

```python
def calculate_state(orange_present, black_present):

    if orange_present and black_present:
        return "BOTH"

    if orange_present:
        return "ORANGE_ONLY"

    if black_present:
        return "BLACK_ONLY"

    return "NONE"
```

---

# 39. Detector de cambio de estado

```python
previous_state = None

while True:

    current_state = calculate_state(
        orange_present,
        black_present
    )

    if current_state != previous_state:

        generate_event(
            previous_state,
            current_state
        )

        previous_state = current_state
```

---

# 40. Eventos

Ejemplos:

```json
{
  "type": "STATE_CHANGE",
  "from": "BOTH",
  "to": "BLACK_ONLY",
  "timestamp": "2026-08-13T21:17:00"
}
```

```json
{
  "type": "PROLONGED_ABSENCE",
  "cat": "orange",
  "duration_seconds": 1800
}
```

---

# 41. Memoria del agente

Persistir:

```text
last_seen_orange
last_seen_black
current_state
previous_state
last_alert_time
daily_presence_time
daily_absence_time
```

Ejemplo:

```json
{
  "orange": {
    "last_seen": "21:45:12",
    "present": true
  },
  "black": {
    "last_seen": "21:32:45",
    "present": false
  }
}
```

---

# 42. Papel del agente

El detector no debe tomar todas las decisiones.

Separar:

```text
YOLO = percepción
Tracker = continuidad
Clasificador = identidad
Motor de estados = realidad observable
Agente = interpretación + decisión
```

Ejemplo:

```text
Percepción:
solo está presente el gato negro

Memoria:
el gato naranja fue visto por última vez hace 35 min

Contexto:
umbral de alerta = 30 min

Decisión:
generar alerta
```

---

# 43. Ejemplo de prompt de sistema

```text
Eres un agente de monitoreo de mascotas.

Tu tarea es interpretar eventos producidos por el sistema de visión.

Nunca inventes que un gato está presente.

Usa únicamente el estado enviado por el detector.

Debes distinguir entre:
- gato naranja
- gato negro

Cuando recibas un cambio de estado:
1. revisa el estado anterior;
2. revisa el estado actual;
3. revisa la última hora de detección;
4. decide si debe emitirse una alerta;
5. evita alertas duplicadas.

No generes una alerta de ausencia por una única detección perdida.
```

---

# 44. Alertas sugeridas

### Aparición

```text
🐈 El gato naranja acaba de aparecer en el área monitoreada.
```

```text
🐈‍⬛ El gato negro acaba de aparecer.
```

### Ambos presentes

```text
✅ Ambos gatos están presentes.
```

### Solo uno

```text
⚠️ Solo está presente el gato negro.
```

### Ninguno

```text
⚠️ No se detectan gatos en el área monitoreada.
```

### Ausencia prolongada

```text
🔴 El gato naranja no ha sido detectado durante 30 minutos.
```

---

# 45. No saturar de alertas

Añadir cooldown.

Ejemplo:

```text
ALERT_COOLDOWN = 60 s
```

Una transición:

```text
BOTH → BLACK_ONLY
```

produce una alerta.

No volver a emitir la misma alerta continuamente mientras el estado se mantenga.

---

# 46. Historial de actividad

Ejemplo:

| Hora | Evento |
|---|---|
| 08:11 | Gato naranja apareció |
| 08:14 | Gato negro apareció |
| 08:14 | Ambos presentes |
| 08:45 | Gato negro dejó el área |
| 09:02 | Gato negro reapareció |
| 10:35 | Ningún gato visible |

---

# 47. Resumen diario

Una función avanzada del agente podría producir:

```text
Resumen diario

Gato naranja:
- Presente: 4 h 17 min
- Ausente: 2 h 43 min
- Apariciones: 11
- Última detección: 21:44

Gato negro:
- Presente: 5 h 02 min
- Ausente: 1 h 58 min
- Apariciones: 8
- Última detección: 21:51
```

---

# 48. Zonas de interés

Se pueden definir regiones:

```text
Sofá
Zona de comida
Puerta
Cama
Ventana
```

Ejemplo:

```text
gato naranja → zona comida
gato negro → sofá
```

Esto permite eventos como:

```text
🐈 El gato naranja permaneció en el área de comida durante 7 minutos.
```

---

# 49. Fases de implementación

## Fase 0 — Compra

Comprar:

```text
Tapo C220
```

Opcional:

```text
microSD 64/128 GB
```

---

## Fase 1 — Cámara

Objetivo:

```text
Tapo App funcionando
```

Tareas:

1. instalar la cámara;
2. conectarla al Wi-Fi;
3. actualizar firmware;
4. crear Camera Account;
5. obtener IP;
6. reservar IP en DHCP.

---

## Fase 2 — RTSP

Objetivo:

```text
VLC reproduce stream1
```

---

## Fase 3 — OpenCV

Objetivo:

```text
Python reproduce video en tiempo real
```

---

## Fase 4 — YOLO

Objetivo:

```text
YOLO detecta class = cat
```

---

## Fase 5 — Conteo

Objetivo:

```text
0 gatos
1 gato
2 gatos
```

---

## Fase 6 — Identidad

Objetivo:

```text
orange_cat
black_cat
```

---

## Fase 7 — Tracking

Objetivo:

```text
mantener identidad durante movimiento
```

---

## Fase 8 — Máquina de estados

Objetivo:

```text
NONE
ORANGE_ONLY
BLACK_ONLY
BOTH
```

---

## Fase 9 — Alertas

Objetivo:

```text
estado cambia
→ alerta
```

---

## Fase 10 — Agente

Objetivo:

```text
eventos
 ↓
LangChain/LangGraph
 ↓
razonamiento
 ↓
acción
```

---

## Fase 11 — MCP

Objetivo:

```text
LangChain
 ↓
MCP Client
 ↓
Tapo MCP
 ↓
Tapo camera
```

Probar:

```text
"Lista mis dispositivos Tapo"
```

y:

```text
"Toma una instantánea de la cámara"
```

---

# 50. MVP mínimo entregable

Para considerar el proyecto exitoso en su primera versión:

```text
✅ video RTSP
✅ detección YOLO
✅ conteo de gatos
✅ identificación naranja / negro
✅ estados
✅ alertas
✅ integración básica con agente
✅ prueba MCP
```

No es obligatorio comenzar con:

```text
❌ control PTZ automático
❌ reconocimiento de conducta
❌ alimentación automática
❌ nube
❌ múltiples cámaras
```

---

# 51. MVP recomendado para la exposición

Demostración:

### Escenario 1

```text
ningún gato
→ NONE
```

### Escenario 2

entra gato naranja:

```text
NONE
 ↓
ORANGE_ONLY
```

Alerta:

```text
🐈 Gato naranja detectado.
```

### Escenario 3

entra gato negro:

```text
ORANGE_ONLY
 ↓
BOTH
```

Alerta:

```text
✅ Ambos gatos están presentes.
```

### Escenario 4

sale el naranja:

```text
BOTH
 ↓
BLACK_ONLY
```

Alerta:

```text
⚠️ Solo permanece el gato negro.
```

---

# 52. Pruebas recomendadas

| Prueba | Resultado esperado |
|---|---|
| Ningún gato | `NONE` |
| Solo naranja | `ORANGE_ONLY` |
| Solo negro | `BLACK_ONLY` |
| Ambos | `BOTH` |
| Gato parcialmente oculto | evitar desaparición instantánea |
| Ambos juntos | detectar 2 individuos |
| Iluminación baja | evaluar precisión |
| Visión nocturna IR | evaluar pérdida de color |
| Cámara pierde Wi-Fi | evento de cámara offline |
| RTSP cae | reconexión |
| Gato sale 1 segundo | no alertar ausencia prolongada |
| Gato ausente 30 min | generar alerta |

---

# 53. Métricas de evaluación

Para la tarea académica se pueden medir:

### Detección

```text
precision
recall
mAP
```

### Identidad

```text
accuracy naranja vs negro
```

### Tiempo real

```text
FPS procesados
latencia
```

### Agente

```text
alertas correctas
falsas alertas
eventos omitidos
```

---

# 54. Criterios de éxito sugeridos

Ejemplo:

```text
Precisión detección gato > 90%
Identificación individual > 90%
Latencia alerta < 5 s
Falsas alertas < 5%
```

Estos valores son metas del proyecto, no garantías del hardware.

---

# 55. Consideraciones de iluminación

## Día

La diferencia:

```text
naranja
vs
negro
```

facilita la clasificación.

## Noche

La cámara puede activar IR y producir imagen monocromática.

La clasificación debe entonces apoyarse también en:

- forma;
- tamaño;
- rostro;
- silueta;
- textura;
- características corporales.

Si la identificación nocturna resulta crítica, la **Tapo C225** merece consideración por su sensor Starlight.

---

# 56. Optimización de rendimiento

No es necesario que el detector procese todos los 30 fps.

Ejemplo:

```text
video = 30 fps
YOLO = 10–15 fps
```

Para monitoreo doméstico puede seguir percibiéndose como tiempo real.

También se puede usar:

```text
stream2
```

para detección rápida y reservar:

```text
stream1
```

para snapshots o evidencia de mayor calidad.

---

# 57. Arquitectura eficiente recomendada

```text
Tapo stream2
  ↓
YOLO
  ↓
eventos

si ocurre evento:
  ↓
capturar imagen de alta calidad
  ↓
guardar evidencia
```

Esto reduce consumo de GPU y red.

---

# 58. Qué NO hacer

No:

```text
enviar cada frame al LLM
```

No:

```text
generar alertas por un frame perdido
```

No:

```text
publicar RTSP en Internet
```

No:

```text
guardar contraseñas dentro del código
```

No:

```text
hacer depender toda la lógica del LLM
```

El agente debe recibir observaciones confiables producidas por la capa de visión.

---

# 59. Posible extensión con un actuador físico

Para hacer aún más evidente la parte de **Physical AI**, se puede añadir:

```text
bombilla Tapo
```

o:

```text
smart plug Tapo
```

Ejemplo:

```text
gato detectado en zona prohibida
       ↓
agente
       ↓
MCP
       ↓
bombilla Tapo
       ↓
cambio de luz
```

Esto permite demostrar:

```text
PERCEPCIÓN
   ↓
RAZONAMIENTO
   ↓
ACCIÓN FÍSICA
```

---

# 60. Diagrama agentic completo

```mermaid
flowchart LR
    ENV[Entorno real] --> CAM[Tapo C220]
    CAM --> RTSP[RTSP]
    RTSP --> CV[OpenCV]
    CV --> YOLO[YOLO]
    YOLO --> TRACK[Tracking]
    TRACK --> ID[Identidad]
    ID --> STATE[Estado]
    STATE --> MEM[Memoria]

    CAM --> MCP[Tapo MCP]
    MCP --> AGENT[LangChain Agent]

    MEM --> AGENT

    AGENT --> ALERT[Alerta]
    AGENT --> DB[Historial]
    AGENT --> DEVICE[Actuador Tapo]
```

---

# 61. Pregunta de investigación técnica

Una formulación posible:

> ¿En qué medida un agente de inteligencia artificial con percepción visual puede identificar y monitorear de forma autónoma la presencia de mascotas en un entorno doméstico mediante una cámara IoT y herramientas de interacción física?

---

# 62. Hipótesis técnica del prototipo

> La combinación de video RTSP, detección mediante YOLO, clasificación individual, memoria temporal y herramientas MCP permitirá implementar un agente capaz de monitorear de manera autónoma la presencia de dos mascotas y generar alertas contextuales ante cambios en el entorno.

---

# 63. Aporte del proyecto

El proyecto integra cuatro dominios:

```text
IoT
+
Computer Vision
+
AI Agents
+
MCP
```

Esto lo convierte en una demostración de:

```text
perception
→ state
→ memory
→ reasoning
→ action
```

---

# 64. Compra recomendada final

## Cámara

**TP-Link Tapo C220**

## Tienda recomendada según revisión del 13/08/2026

**Compupal Perú**

## Precio observado

```text
S/ 95.15
```

## Stock mostrado

```text
9 unidades
```

## Enlace

https://www.compupalperu.com/producto/camara_ip_tplink_tapo_c220

---

# 65. Lista de compra sugerida

### Obligatorio

- 1 × Tapo C220
- conexión Wi-Fi 2.4 GHz
- computadora para procesamiento
- Python
- VLC

### Recomendado

- microSD 64–128 GB
- soporte / ubicación elevada
- conexión estable
- iluminación ambiental suficiente

### Opcional

- bombilla Tapo
- smart plug Tapo
- Raspberry Pi / mini PC Linux para alojar MCP

---

# 66. Checklist previo a compra

- [ ] Confirmar que el modelo sea C220
- [ ] Confirmar garantía
- [ ] Confirmar stock
- [ ] Confirmar precio final
- [ ] Confirmar delivery
- [ ] Conservar comprobante
- [ ] Verificar que RTSP esté disponible en la versión de hardware/firmware
- [ ] Actualizar firmware después de instalar

---

# 67. Checklist de implementación

- [ ] Cámara configurada en Tapo App
- [ ] IP conocida
- [ ] IP reservada en router
- [ ] Camera Account creado
- [ ] RTSP funciona en VLC
- [ ] RTSP funciona en OpenCV
- [ ] YOLO detecta gatos
- [ ] Conteo 0 / 1 / 2 funciona
- [ ] Se distingue naranja / negro
- [ ] Tracking habilitado
- [ ] Máquina de estados implementada
- [ ] Persistencia temporal implementada
- [ ] Alertas implementadas
- [ ] MCP funcionando
- [ ] LangChain conectado al MCP
- [ ] Demo completa preparada

---

# 68. Orden recomendado de trabajo

No comenzar por MCP.

Orden:

```text
1. Comprar cámara
2. RTSP
3. OpenCV
4. YOLO
5. Identidad
6. Tracking
7. Estados
8. Alertas
9. Agente
10. MCP
11. Actuador opcional
```

Esto reduce considerablemente el riesgo técnico.

---

# 69. Riesgos del proyecto

| Riesgo | Solución |
|---|---|
| pérdida de color por IR | entrenar también con imágenes nocturnas |
| oclusión | tracking + timeout |
| falsa detección | threshold de confianza |
| RTSP interrumpido | reconexión automática |
| IP cambia | reserva DHCP |
| alertas repetidas | cooldown |
| cámara sin red | watchdog |
| MCP no descubre en Docker Windows | Linux/native networking |
| credenciales expuestas | `.env` y secretos |
| LLM inventa estado | usar datos estructurados como fuente de verdad |

---

# 70. Conclusión

El proyecto es **altamente viable**.

La solución recomendada es:

```text
Tapo C220
    ↓
RTSP
    ↓
OpenCV
    ↓
YOLO
    ↓
Tracking
    ↓
Identificación naranja / negro
    ↓
Motor de estados
    ↓
Memoria temporal
    ↓
LangChain / LangGraph
    ↓
MCP
    ↓
Alerta / acción física
```

La **Tapo C220** es actualmente la mejor opción para este proyecto por:

- resolución 4 MP;
- video 2K;
- hasta 30 fps;
- RTSP;
- ONVIF;
- compatibilidad declarada por el proyecto Tapo;
- precio cercano a S/ 95–106 en Perú;
- disponibilidad local;
- muy buena relación costo/prestaciones.

Para una primera demostración, el objetivo debe ser:

```text
reconocer
→ identificar
→ mantener estado
→ detectar cambio
→ alertar
```

Después se pueden añadir:

```text
tracking avanzado
zonas
resúmenes
control PTZ
actuadores
múltiples cámaras
```

---

# 71. Fuentes consultadas

## TP-Link Perú — Tapo C220
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c220/

## TP-Link Perú — Tapo C210
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c210/

## TP-Link Perú — Tapo C225
https://www.tp-link.com/pe/home-networking/cloud-camera/tapo-c225/

## TP-Link Perú — RTSP / ONVIF
https://www.tp-link.com/pe/support/faq/4465/

## TP-Link — configuración RTSP
https://www.tp-link.com/es/support/faq/2680/

## Tapo API / MCP
https://github.com/mihai-dinculescu/tapo

## Tapo MCP
https://github.com/mihai-dinculescu/tapo/tree/main/tapo-mcp

## Dispositivos soportados
https://github.com/mihai-dinculescu/tapo/blob/main/SUPPORTED_DEVICES.md

## LangChain MCP
https://docs.langchain.com/oss/python/langchain/mcp

## LangChain MCP Adapters
https://github.com/langchain-ai/langchain-mcp-adapters

## Compupal Perú — C220
https://www.compupalperu.com/producto/camara_ip_tplink_tapo_c220

## Arteus — C220
https://arteus.pe/products/tp-link-tapo-c220-camara-de-seguridad-wifi-4mp-2k-360%C2%BA-pt

## Memory Kings — C225
https://www.memorykings.pe/producto/347086/camara-cloud-wifi-tp-link-tapo-c225-2k-qhd-p-t-msd

---

# Nota final sobre precios

Los precios y existencias mencionados fueron observados el **13 de agosto de 2026** y pueden cambiar sin previo aviso.

Antes de comprar, verificar nuevamente:

```text
precio
stock
garantía
versión de hardware
delivery
```
