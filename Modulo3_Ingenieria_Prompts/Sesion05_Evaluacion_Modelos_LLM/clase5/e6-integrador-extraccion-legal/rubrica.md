# Rúbrica · e6 — Extracción legal (todo binario)

El prompt-contrato se evalúa como código: o cumple el esquema o no. Hay dos niveles.

---

## Nivel BÁSICO (Individual) — `contrato-basico.md` → `esquema-basico.json`

1. - [ ] **Parsea** — JSON sintácticamente válido (`json.loads` sin error). *ELIMINATORIO.*
2. - [ ] **Claves 100%** — todas las del molde, ninguna de más ni de menos.
3. - [ ] **Tipos 100%** — string / number / array / null según el molde.
4. - [ ] **Valores correctos** (Servicios Globales):
       - empleador: `Servicios Globales S.A.C.` · RUC `20123456789` · representante `Luis Alberto Ramírez Vargas`
       - trabajadora: `Ana Sofía Morales Pérez` · DNI `87654321` · `Jr. Los Jazmines 456, Surco, Lima`
       - cargo `Coordinadora de Proyectos Digitales` · inicio `2025-03-01` · fin `2026-02-28`
       - remuneración `7500 PEN` · `duracion_meses` `12` · beneficios: gratificaciones jul/dic, vacaciones 30 días, EsSalud

**Aprueba el básico** si parsea + claves + tipos + valores correctos.

---

## Nivel AVANZADO (Equipo) — `contrato-avanzado.md` → `plantilla_contrato.json` (camelCase)

1. - [ ] **Parsea** — JSON válido. *ELIMINATORIO.*
2. - [ ] **Claves y estructura 100%** — coincide con `plantilla_contrato.json` (camelCase, anidamiento exacto).
3. - [ ] **Tipos 100%** — números, strings, arrays y null según el molde.
4. - [ ] **Resolvió la ENMIENDA** — `sueldosBase` tiene **DOS tramos**: `6800 USD` (2024-02-12 → 2025-02-28)
       y `7200 USD` (2025-03-01 → null). *Es el punto que más se falla.*
5. - [ ] **Vesting correcto** — `opciones`: 6000 a USD 12; vesting 25 % en 2025-02-12 + 75 % mensual a 36 meses
       (los porcentajes suman 100 %).
6. - [ ] **Cláusulas especiales** — `noCompetencia` (9 meses, Latinoamérica, 2 excepciones),
       `leyAplicable` "Argentina", `rolProteccionDatos` "encargada del tratamiento".
7. - [ ] **Política de faltantes** — lo que NO está explícito sale como `null` (p. ej. `empleado.*` se
       extrae del contrato; lo no presente jamás se inventa).

**Aprueba el avanzado** si cumple 1–7. Los puntos 4 y 5 (enmienda + vesting) son el corazón del reto.

## Solución de referencia (avanzado)
Ver `plantilla_contrato.json` — trae los valores esperados de `puesto`, `sueldosBase`, `compVariable`,
`mesesPrueba`, `noCompetencia`, `opciones`, `leyAplicable` y `rolProteccionDatos`. Los campos de
`empleado` se extraen del contrato: `María de la Paz González López`, DNI `26.654.789`,
`C/ Atocha 45, 3 A, Madrid, España`.

> El corazón del ejercicio (ambos niveles) conecta con el caso del abogado: un dato ausente se declara
> `null`, jamás se inventa. La diferencia del avanzado es **resolver la enmienda y los anexos**.
