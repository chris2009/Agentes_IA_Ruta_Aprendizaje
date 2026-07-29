# Paso 1 de 3 · Resumen

> **Su input es el texto original** (`texto-fuente.md`). Es el único paso que recibe la entrada
> externa. **Su salida (el resumen) será el input del Paso 2.** Corre este prompt en el chat, copia la
> salida y guárdala: la pegarás en `paso2-traduccion.md`.

---

```
Eres un asistente que resume textos de forma concisa y factual. Resume el siguiente texto en MÁXIMO
3 oraciones, sin opiniones ni información que no esté en el texto. Conserva el idioma original
(español). Devuelve SOLO el resumen, sin encabezados ni comentarios.

<<<
{pega aquí el contenido de texto-fuente.md}
>>>
```

---

**Contrato de salida del Paso 1:** texto plano, máximo 3 oraciones, en el idioma original (español),
sin opiniones ni datos inventados. Esta salida es la **entrada del Paso 2 (traducción)**.
