# Input · tarea grande (el mega-prompt de RRHH)

Un equipo de selección usa **UN solo prompt** al que le pega el CV de un candidato y, **de una sola
pasada**, debe hacer todo esto:

> **Mega-prompt actual (todo de una vez):**
>
> "Eres el asistente de selección de la empresa. Recibes el CV de un candidato para el puesto de
> Analista de Datos. Haz TODO esto en una sola respuesta: (1) **evalúa** si cumple los requisitos
> mínimos del puesto (Python, SQL, 2+ años de experiencia, inglés intermedio); (2) **puntúa** al
> candidato en 4 dimensiones del 1 al 5: experiencia técnica, habilidades blandas, alineación
> cultural y expectativa salarial; (3) **redacta** el correo de respuesta al candidato informándole
> si avanza o no a la siguiente etapa; (4) **verifica** que el correo cumpla las políticas de RRHH
> (no mencionar edad, género, estado civil o religión; no hacer promesas de sueldo; mantener tono
> empático y profesional). Devuélvelo todo junto."

---

El problema: funciona cuando el CV es claro. Cuando no lo es —experiencia ambigua, sueldo no
declarado, perfil parcial— alguna de las 4 tareas falla **en algún lado** y nadie sabe en cuál:
¿evaluó mal los requisitos? ¿el puntaje no refleja la evaluación? ¿el correo prometió algo
indebido? ¿la verificación fue real?

## Tu tarea
Toma este mega-prompt y **pártelo en 2–4 pasos consecutivos**, donde cada paso hace **una** sola
cosa y **procesa la salida del anterior**. Para cada paso, nombra su **contrato de salida**: qué
entrega y en qué formato. Marca dónde un error de un paso contaminaría al siguiente (dónde iría
un *gate*).
