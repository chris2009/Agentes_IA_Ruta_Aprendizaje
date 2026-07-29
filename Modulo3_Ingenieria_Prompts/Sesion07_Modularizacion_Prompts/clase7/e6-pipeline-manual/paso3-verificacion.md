# Paso 3 de 3 · Verificación bilingüe (el gate)

> **Sus inputs son DOS salidas anteriores:** el RESUMEN del Paso 1 y la TRADUCCIÓN del Paso 2. Este es
> el **gate** del pipeline: devuelve un **JSON parseable** que decide si la traducción se aprueba, se
> rehace o se escala. Corre este prompt pegando ambos textos.

---

```
Eres un verificador de consistencia bilingüe. Compara el RESUMEN ORIGINAL (español) con su TRADUCCIÓN
(inglés) y determina si la traducción es FIEL: que no omita información ni cambie el significado.

Devuelve SOLO un objeto JSON válido, sin texto fuera del JSON, con EXACTAMENTE estas claves:
{
  "faithful": boolean,                 // true si la traducción es fiel al resumen
  "missing_info": [string],            // datos del resumen que la traducción omitió (vacío si ninguno)
  "changes_of_meaning": [string],      // cambios de sentido detectados (vacío si ninguno)
  "action": "approve" | "revise"       // "approve" si faithful=true; "revise" si faithful=false
}

RESUMEN ORIGINAL (salida del Paso 1):
<<<
{pega aquí el resumen del Paso 1}
>>>

TRADUCCIÓN A VERIFICAR (salida del Paso 2):
<<<
{pega aquí la traducción del Paso 2}
>>>
```

---

**Contrato de salida del Paso 3:** un JSON parseable con `faithful`, `missing_info`,
`changes_of_meaning` y `action`. Sobre este JSON se aplica la **regla del gate** (ver
`INSTRUCCIONES.md`):

```
if action == "approve":            -> el pipeline termina OK
if action == "revise" and retries <  max_retries (2):  -> rehacer el Paso 2 usando missing_info / changes_of_meaning como instrucción
if action == "revise" and retries >= max_retries (2):  -> escalate (a un revisor humano)
```
