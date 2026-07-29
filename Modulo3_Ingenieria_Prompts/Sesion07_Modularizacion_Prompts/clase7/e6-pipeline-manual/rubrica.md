# Rúbrica · e6 ESTRELLA — Pipeline manual (binaria)

El estrella integra todo lo de la clase: chaining (e1), contrato + gate (e2), y observabilidad. Todo
criterio es **binario** — se cumple o no.

## Criterios de aprobación
- [ ] **Encadenó los 3 pasos pasando la salida de uno como entrada del siguiente** — la entrada del
      Paso 2 es la **salida del Paso 1** (el resumen), no el texto original; y la entrada del Paso 3
      son las salidas del Paso 1 **y** del Paso 2. (Si pegó el texto original en el Paso 2, **no
      cumple**: no hubo encadenamiento.)
- [ ] **El verificador devolvió un JSON parseable** — un objeto JSON válido con al menos las claves
      `faithful` y `action`. Un párrafo de opinión **no cumple**.
- [ ] **Se aplicó la regla del gate al menos una vez** — se leyó `action` y se actuó: `approve`
      termina; `revise` rehace el Paso 2; reintentos agotados → `escalate`. Debe verse al menos una
      decisión del gate (idealmente, al menos un `revise` provocado — ver INSTRUCCIONES).
- [ ] **Reportó al menos una métrica de observabilidad** — el **revise rate del paso de traducción**
      sobre las corridas hechas, y **nombró el paso más débil**.

## Cómo verificar cada criterio (rápido)
| Criterio | Cómo lo compruebas |
|----------|--------------------|
| Encadenamiento | Pide ver las 3 entradas: la del Paso 2 debe ser el resumen del Paso 1, no el texto fuente. |
| JSON válido | Copia el JSON del verificador y pégalo en cualquier validador de JSON (o en el Colab); debe parsear. |
| Gate aplicado | Hay una decisión registrada (approve / revise→rehacer / escalate). |
| Métrica | Hay una tabla con ≥ 1 corrida y un revise rate calculado + el paso más débil nombrado. |

## El resultado esperado (referencia)
- **Resumen (Paso 1):** ~3 oraciones en español que recogen: el mega-prompt como caja negra → la
  alternativa de descomponer en pasos encadenados (Anthropic 2024) → las ventajas (precisión,
  depuración, formato estable, mantenimiento) y el gate que detiene la propagación.
- **Traducción (Paso 2):** el mismo resumen en inglés, fiel.
- **Verificación (Paso 3):** si la traducción es fiel → `{"faithful": true, "missing_info": [],
  "changes_of_meaning": [], "action": "approve"}`. Si se forzó una omisión → `faithful: false` con la
  omisión listada en `missing_info` y `action: "revise"`.

> Nota: no se exige que la traducción sea perfecta a la primera; **el aprendizaje es el procedimiento**
> — encadenar, verificar con el gate, y aplicar revise/escalate. Que el gate **dispare** y se actúe
> sobre él vale más que un approve directo.

## El punto clave (lo que se discute en clase)
Hacer esto a mano demuestra que **prompt chaining no requiere framework**: la estructura (pasos +
contratos + gate) es lo que importa, no la herramienta. El **Colab con LangChain** es la misma idea
automatizada — útil para medir a escala, pero **opcional**.

**Aprueba** si encadenó los 3 pasos (salida→entrada), el verificador devolvió JSON parseable, se
aplicó la regla del gate al menos una vez, y se reportó el revise rate del paso de traducción con el
paso más débil nombrado.
