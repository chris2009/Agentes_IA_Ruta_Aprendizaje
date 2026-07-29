# Prompt-plantilla · e2 — Verificar condiciones (anti-alucinación)

> Táctica 3 del Principio 1. UN SOLO prompt debe comportarse bien en los DOS inputs:
> reescribir los pasos cuando existen, y declarar el caso vacío cuando no existen — sin inventar.
> Ejecútalo dos veces, una con `texto-con-pasos.md` y otra con `texto-sin-pasos.md`.

```
Lee el contenido entre <doc></doc>.

Si el texto contiene una secuencia de PASOS o instrucciones de un procedimiento, reescríbela
como una lista numerada (Paso 1, Paso 2, ...), usando solo la información presente en el texto.

Si el texto NO contiene pasos (por ejemplo, es una descripción o una opinión), responde
EXACTAMENTE con esta frase y nada más:

  No se encontraron pasos.

No inventes pasos que no estén en el texto.

<doc>
{pega aquí el contenido del archivo de input}
</doc>
```
