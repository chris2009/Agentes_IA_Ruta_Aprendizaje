# Entorno virtual compartido del módulo `Modulo4_Agentes_Cognitivos`

Este módulo usa **un único entorno virtual** (`.venv`) ubicado en la raíz del módulo, compartido por todas las sesiones (`Sesion8_Arquitectura_Agentes`, `Sesion9_Agentes_Memoria_Contextual`, `Sesion10`, y cualquier sesión futura). Así no hay que crear un venv distinto por carpeta.

Un **entorno virtual** (*virtual environment*, comúnmente llamado *venv*) es una copia aislada del intérprete de Python con su propio conjunto de paquetes instalados, independiente del Python global del sistema. Esto evita que las dependencias de un proyecto choquen con las de otro.

## Ubicación

```
D:\APRENDIZAJE\PROGRAMA_IMPLEMENTACION_AGENTES_IA\Modulo4_Agentes_Cognitivos\.venv
```

En WSL (*Windows Subsystem for Linux*, la capa que permite correr Linux dentro de Windows), esa misma ruta se accede como:

```
/mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo4_Agentes_Cognitivos/.venv
```

## Cómo activarlo (desde cualquier sesión)

No importa en qué subcarpeta estés parado (`Sesion9_Agentes_Memoria_Contextual`, `Sesion10/agents26_m4s10-main`, etc.) — activar un venv solo requiere darle la ruta completa al script `activate`, no hace falta hacer `cd` hasta la carpeta del venv:

```bash
source /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo4_Agentes_Cognitivos/.venv/bin/activate
```

Sabrás que quedó activo porque el prompt de la terminal cambia a algo como:

```
(.venv) xtian@DESKTOP-KHH3I66:~$
```

Para desactivarlo:

```bash
deactivate
```

## Verificar que todo está bien

Después de activar, confirma que Python y `pip` (el instalador de paquetes de Python) apuntan al venv correcto y no a otro intérprete del sistema:

```bash
which python
python -m pip show langchain
```

`which python` debe devolver una ruta dentro de `Modulo4_Agentes_Cognitivos/.venv/bin/python`. Si devuelve otra cosa (por ejemplo, una ruta de `pyenv`, el gestor de versiones de Python), algo salió mal con la activación.

## Instalar o actualizar paquetes

Con el venv activado:

```bash
pip install -r requirements.txt
```

El archivo [requirements.txt](requirements.txt) en esta misma carpeta contiene la lista congelada (*freeze*) de todos los paquetes ya instalados (LangChain, LangGraph, el adaptador de Ollama, etc.). Si instalas algo nuevo y quieres que quede documentado para el futuro:

```bash
pip install nombre-del-paquete
pip freeze > requirements.txt
```

## Ejecutar un script de cualquier sesión

Con el venv activado, simplemente corre el script normal, sin importar en qué carpeta del módulo estés:

```bash
cd /mnt/d/APRENDIZAJE/PROGRAMA_IMPLEMENTACION_AGENTES_IA/Modulo4_Agentes_Cognitivos/Sesion10/agents26_m4s10-main
python 00_basic_agent.py
```

## ⚠️ Regla importante: nunca renombres ni muevas la carpeta `.venv` (ni su carpeta padre)

Un venv creado con el módulo estándar `venv` de Python **graba rutas absolutas como texto fijo** dentro de varios de sus archivos internos:

- `.venv/bin/activate` — graba la variable `VIRTUAL_ENV` con la ruta absoluta de creación.
- `.venv/bin/pip` (y cualquier otro script de consola instalado) — tiene una primera línea (*shebang*) con la ruta absoluta del intérprete Python que debe usar.

Si renombras o mueves la carpeta que contiene `.venv` **después** de crearlo, esas rutas quedan apuntando a un lugar que ya no existe:

- `activate` deja de agregar correctamente el venv al `PATH` (variable que le dice a la terminal dónde buscar comandos), y la terminal termina usando otro Python del sistema sin que te des cuenta (el prompt puede seguir mostrando `(.venv)` aunque en realidad no lo esté usando).
- `pip` deja de ejecutarse directamente, con un error tipo `cannot execute: required file not found`.

**Si necesitas reorganizar carpetas**, la forma segura es:

```bash
# 1. Congela los paquetes actuales usando el python del venv directamente (no pip, por si ya está roto)
/ruta/vieja/.venv/bin/python -m pip freeze > requirements.txt

# 2. Crea el venv nuevo en el destino final
cd /ruta/nueva
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Borra el venv viejo (ya no sirve)
rm -rf /ruta/vieja/.venv
```

Esto es exactamente lo que se hizo para migrar el entorno original (creado en `Modulo4_Arquitectura_Agentes/Sesion9`) al actual `Modulo4_Agentes_Cognitivos/.venv`.

## Glosario

- **Entorno virtual (venv)**: copia aislada del intérprete de Python con sus propios paquetes instalados, independiente del sistema.
- **WSL** (*Windows Subsystem for Linux*): capa de compatibilidad que permite ejecutar un entorno Linux directamente dentro de Windows.
- **PATH**: variable de entorno que le indica a la terminal en qué carpetas buscar los programas que se ejecutan por nombre (como `python` o `pip`).
- **Shebang**: primera línea de un script (`#!/ruta/al/interprete`) que indica con qué programa debe ejecutarse.
- **pip**: el instalador de paquetes estándar de Python.
- **freeze**: comando de `pip` (`pip freeze`) que lista todos los paquetes instalados junto con su versión exacta, típicamente guardado en `requirements.txt`.
