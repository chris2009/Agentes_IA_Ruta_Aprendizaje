# Prompt-maestro · e6 nivel AVANZADO (Equipo) — Extracción legal → JSON exacto

> Input: `contrato-avanzado.md` (Epsilon Robotics, 4 págs con anexos y enmienda). Objetivo: extraer
> a un JSON que cumpla EXACTAMENTE `plantilla_contrato.json` (camelCase). Aplica TODO: delimitadores +
> salida estructurada + faltantes=`null` + especificar pasos. Pega el contrato entre `<doc></doc>`.
>
> El reto del avanzado: (a) **resolver la enmienda** (el sueldo base cambia → `sueldosBase` tiene 2
> tramos), (b) leer **anexos** (opciones/vesting, protección de datos), (c) no inventar lo que no esté.

Este ejercicio se puede resolver con UN prompt maestro, o descomponerlo en 3 sub-prompts por sección
(diseño "prompt de referencia"):

| Sub-prompt | Procesa | Rol sugerido | Devuelve |
|---|---|---|---|
| **A — Partes & Puesto** | Secciones 1–2 | "Abogado Laboral Junior" | `empleado`, `puesto` |
| **B — Remuneración** | Sección 3 + Primera Enmienda | "Especialista Comp&Ben" | `sueldosBase[]` (2 tramos), `compVariable`, `mesesPrueba` |
| **C — Cláusulas especiales** | Secciones 7–9 + Anexos A/B | "Analista de Cláusulas" | `clausulaConfidencialidad`, `noCompetencia`, `opciones`, `leyAplicable`, `rolProteccionDatos` |
| **Maestro** | Todo el documento | "LegalDataParser Senior" | el JSON completo; valida que el vesting sume 100 % |

## Prompt maestro (un solo paso)

```
Actúa como LegalDataParser Senior. Extrae los datos del contrato laboral (con sus anexos y enmienda)
que está entre <doc></doc> y devuélvelos EXCLUSIVAMENTE como un JSON que cumpla EXACTAMENTE el molde
de plantilla_contrato.json (camelCase): mismas claves, misma estructura anidada, mismos tipos.
No agregues claves ni texto fuera del JSON.

Razona internamente entre etiquetas <pensamiento>...</pensamiento> y NO incluyas ese bloque en la
salida final (solo el JSON).

Procede así:
  Paso 1: localiza cada dato en el texto (incluyendo Anexos y la Primera Enmienda).
  Paso 2: RESUELVE la enmienda. La Sección 3.1 fue sustituida: `sueldosBase` debe tener DOS tramos
          — USD 6 800 del 2024-02-12 al 2025-02-28, y USD 7 200 desde 2025-03-01 (fin: null).
  Paso 3: para el vesting de `opciones`, refleja 25 % en una fecha fija + 75 % mensual a 36 meses;
          verifica que los porcentajes sumen 100 %.
  Paso 4: si un dato NO aparece explícitamente, asigna null. NO inventes ni deduzcas.

Molde de salida: el de plantilla_contrato.json (empleado, puesto, sueldosBase[], compVariable,
mesesPrueba, clausulaConfidencialidad, noCompetencia, opciones, leyAplicable, rolProteccionDatos).

<doc>
{pega aquí el contenido de contrato-avanzado.md}
</doc>
```
