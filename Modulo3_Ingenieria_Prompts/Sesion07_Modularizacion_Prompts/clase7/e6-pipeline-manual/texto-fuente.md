# Input · texto fuente (~1 página, para resumir)

Este es el **texto de entrada del pipeline**. Es el único input externo: a partir de aquí, cada paso
consume la salida del anterior. Cópialo donde lo indique `paso1-resumen.md`.

> Puedes reemplazarlo por cualquier texto de ~1 página (un artículo, una política, un correo largo).
> Para la clase usamos este, sobre el propio tema del curso.

---

## El paso del mega-prompt al pipeline modular

Durante los primeros años de adopción de los modelos de lenguaje, el patrón dominante fue el
"mega-prompt": una sola instrucción, a veces de varios párrafos, que le pedía al modelo resolver una
tarea compleja de una sola pasada. Un equipo de soporte, por ejemplo, escribía un único prompt que
debía clasificar el correo de un cliente, traducirlo si venía en otro idioma, redactar una respuesta y
verificar que esa respuesta cumpliera la política de la empresa. El enfoque era atractivo por su
simplicidad aparente: un prompt, una llamada, un resultado.

El problema apareció con la escala. Estos mega-prompts funcionaban una parte de las veces, pero cuando
fallaban, fallaban de forma opaca: nadie podía decir en qué momento se había torcido el resultado. ¿El
modelo clasificó mal el correo? ¿Tradujo con un error que arrastró al resto? ¿Inventó una cláusula de
la política que no existía? Como todo ocurría dentro de una sola llamada, no había manera de
inspeccionar los pasos intermedios. El sistema era, en la práctica, una caja negra: producía una
salida final sin dejar rastro de cómo había llegado a ella.

La alternativa que se consolidó fue descomponer la tarea en una secuencia de pasos más pequeños, donde
cada paso hace una sola cosa y procesa la salida del anterior. En lugar de un prompt que "resume,
traduce y verifica de una vez", se encadenan tres pasos: primero un resumen, luego una traducción de
ese resumen, y por último una verificación que compara ambos. Anthropic, en su guía de 2024, llamó a
este patrón "encadenamiento de prompts" y señaló que intercambia algo de latencia por una mayor
precisión, porque cada llamada del modelo enfrenta una tarea más fácil y acotada.

Esta modularidad trae cuatro ventajas concretas. La primera es precisión por paso: un prompt que hace
una sola cosa tiene menos ambigüedad y acierta más. La segunda es la depuración localizada: si algo
falla, se sabe exactamente en qué paso, no "en algún lado". La tercera es el formato estable entre
pasos, porque cada paso entrega una salida con una forma conocida que el siguiente consume sin
sorpresas. La cuarta es la facilidad de mantenimiento: se puede reemplazar un módulo —traducir con
otro proveedor, por ejemplo— sin reescribir todo el sistema.

Para que la cadena sea confiable, entre paso y paso se inserta un "gate": una regla que evalúa la
salida de un paso y decide si el proceso continúa, se rehace o se escala a una persona. El gate cumple
una función crítica: detiene la propagación de errores. Sin él, un resumen que omitió un dato
contamina la traducción y la verificación que vienen después; la cadena es tan fuerte como su eslabón
más débil. Y donde el riesgo lo amerita, el gate puede transferir el control a un humano, que deja de
ser una señal de fracaso para convertirse en una pieza de diseño del sistema.
