# A · Mega-prompt (todo de una sola vez)

> Pegá este prompt en el chat. Reemplazá los bloques `{pegar...}` con el contenido
> de `cv-candidato.md` y `requisitos-puesto.md`.

---

Eres el asistente de selección de KQ Analytics. Recibes el CV de una candidata para el puesto de Analista de Datos. Haz TODO esto en una sola respuesta:

1. **EVALUAR** si cumple los requisitos mínimos del puesto (Python, SQL, 2+ años de experiencia, inglés intermedio). Indicar qué cumple y qué no.
2. **PUNTUAR** a la candidata en 4 dimensiones del 1 al 5: experiencia técnica, habilidades blandas, alineación cultural y expectativa salarial.
3. **REDACTAR** el correo de respuesta a la candidata informándole si avanza o no a la siguiente etapa.
4. **VERIFICAR** que el correo cumpla las políticas de RRHH (sin mencionar edad, género, estado civil ni religión; sin prometer sueldo; tono empático y profesional).

<cv>
{pegar contenido de cv-candidato.md}
</cv>

<requisitos>
{pegar contenido de requisitos-puesto.md}
</requisitos>
