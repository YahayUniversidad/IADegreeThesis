"""Cliente CLI simple para interactuar con el chatbot."""

import requests
import sys

CHATBOT_URL = "http://127.0.0.1:8001/chat"


def main():
    print("=== Chatbot RAG - Tesis Datamart ===")
    print("Escribe tu pregunta sobre la base de datos o datamart.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            question = input("Tu pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego!")
            break

        if not question or question.lower() in ("salir", "exit", "quit"):
            print("Hasta luego!")
            break

        try:
            resp = requests.post(
                CHATBOT_URL,
                json={"question": question, "execute_sql": True},
                timeout=60,
            )
            data = resp.json()

            print(f"\n{data['response']}")

            if data.get("sql"):
                print(f"\n[SQL ejecutado]: {data['sql']}")

            if data.get("query_results") and not data["query_results"].get("error"):
                qr = data["query_results"]
                print(f"[Resultados: {qr['count']} filas]")

            print()
        except requests.ConnectionError:
            print("Error: No se puede conectar al chatbot. Asegurate de que esta corriendo.")
            print("Ejecuta: python run_servers.py")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
