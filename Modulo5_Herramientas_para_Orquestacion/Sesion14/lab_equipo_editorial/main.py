from editor_jefe_agent import editor_jefe
from _utils import extraer_texto

TEMA = "El impacto de la IA generativa en los empleos de desarrollo de software junior"

if __name__ == "__main__":
    print(f"[EQUIPO EDITORIAL] Tema asignado: {TEMA}\n")
    resultado = editor_jefe.invoke({"messages": TEMA})
    articulo_final = extraer_texto(resultado["messages"][-1])

    print("\n" + "=" * 70)
    print("ARTICULO FINAL")
    print("=" * 70)
    print(articulo_final)
