# Paso 2 de 3 · Traducción

> **Su input es la SALIDA del Paso 1** (el resumen que copiaste), **no** el texto original. Aquí se ve
> el encadenamiento: la salida de un paso es la entrada del siguiente. **Su salida (la traducción)
> será uno de los dos inputs del Paso 3 (verificación).** Corre este prompt, copia la traducción y
> guárdala junto con el resumen del Paso 1.

---

```
Eres un traductor profesional. Traduce al INGLÉS el siguiente RESUMEN, manteniendo la precisión, el
significado y un tono formal. No agregues ni omitas información respecto del resumen. Devuelve SOLO la
traducción, sin encabezados ni comentarios.

RESUMEN A TRADUCIR (salida del Paso 1):
<<<
{pega aquí la salida del Paso 1 (el resumen)}
>>>
```

---

**Contrato de salida del Paso 2:** texto plano en inglés, fiel al resumen del Paso 1 (sin agregar ni
omitir). Esta salida, **junto con el resumen del Paso 1**, son los dos inputs del **Paso 3
(verificación)**.

> **Idioma objetivo:** aquí usamos inglés para que la clase pueda auditar la fidelidad. Si prefieres
> otro idioma, cámbialo en la primera línea del prompt — el pipeline funciona igual.
