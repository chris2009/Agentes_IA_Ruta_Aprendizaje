# C · Del mega-prompt al pipeline — descomposición resuelta

> Este es el entregable que el alumno debe producir en e1.
> Mostrarlo cuando los alumnos terminaron su propio diseño, para contrastar.
> NO mostrarlo antes — es la respuesta.

---

## El mega-prompt original (todo de una vez)

```
Eres el asistente de selección. Recibes el CV de una candidata para Analista de Datos.
Haz TODO esto en una sola respuesta:
  1) evalúa si cumple los requisitos mínimos
  2) puntúa en 4 dimensiones del 1 al 5
  3) redacta el correo de respuesta (avanza / no avanza)
  4) verifica que el correo cumpla las políticas de RRHH
```

**El problema:** si el correo sale mal, no sabés si fue porque evaluó mal los requisitos,
porque el puntaje fue erróneo, o porque la verificación fue falsa. No hay pasos. Es una caja negra.

---

## PIPELINE PROPUESTO

- **Paso 1 · Evaluar requisitos mínimos**
  - Entrada: CV del candidato + requisitos del puesto
  - Salida (contrato):
    ```json
    {
      "cumple_minimos": true | false,
      "requisitos": {
        "python": true | false,
        "sql": true | false,
        "experiencia_anios": <número>,
        "experiencia_cumple": true | false,
        "ingles_intermedio": true | false
      },
      "gaps": ["<requisito no cumplido con explicación>"],
      "nota_ambiguedades": "<qué no está claro en el CV>"
    }
    ```

- **Paso 2 · Puntuar en 4 dimensiones**
  - Entrada: CV + JSON del Paso 1
  - Salida (contrato):
    ```json
    {
      "experiencia_tecnica": <1-5>,
      "habilidades_blandas": <1-5>,
      "alineacion_cultural": <1-5>,
      "expectativa_salarial": <1-5>,
      "puntaje_total": <suma>,
      "avanza": true | false,
      "justificacion_breve": "<1 línea>"
    }
    ```

- **Paso 3 · Redactar correo al candidato**
  - Entrada: JSON del Paso 2 (`avanza` + puntuaciones)
  - Salida (contrato): texto plano del correo de respuesta

- **Paso 4 · Verificar políticas de RRHH**
  - Entrada: borrador del Paso 3 + políticas de la empresa
  - Salida (contrato):
    ```json
    {
      "veredicto": "CUMPLE" | "NO CUMPLE",
      "politica_datos_sensibles": "OK" | "VIOLA",
      "politica_salarial": "OK" | "VIOLA",
      "politica_tono": "OK" | "VIOLA",
      "politica_motivo": "OK" | "VIOLA",
      "action": "approve" | "revise",
      "detalle": "<qué viola exactamente, o 'Todo en regla'>"
    }
    ```

---

## PUNTOS DE GATE

**Gate 1 — entre Paso 1 y Paso 2:**
Si `cumple_minimos = false` → el Paso 2 no corre.
Se redacta directamente un correo de rechazo sin necesidad de puntuar.
Sin este gate, el Paso 3 podría redactar un correo de "avanza" para alguien
que no cumple ni los requisitos mínimos.

**Gate 2 — entre Paso 3 y el envío al candidato:**
El Paso 4 actúa como verificador independiente.
Si `action = revise` → el correo NO se envía; se vuelve al Paso 3 con el `detalle` como contexto.
Sin este gate, un correo que menciona el rango salarial o usa un tono inadecuado
llegaría directo al candidato.

---

## Por qué esto es mejor que el mega-prompt

| Pregunta | Mega-prompt | Pipeline |
|---|---|---|
| ¿Evaluó bien los requisitos? | No se puede saber | Paso 1 → JSON verificable |
| ¿El puntaje refleja la evaluación? | No se puede saber | Paso 2 usa el JSON del Paso 1 |
| ¿El correo viola alguna política? | El modelo se auditó a sí mismo | Paso 4 es un contexto aislado |
| Si algo falló, ¿dónde busco? | En ningún lado | En el paso que devolvió el error |
