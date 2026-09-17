"""Punto de entrada: levanta el MCP Server y el Chatbot RAG."""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Levanta los servidores del sistema RAG")
    parser.add_argument("--mcp-port", type=int, default=8000, help="Puerto del MCP Server")
    parser.add_argument("--chat-port", type=int, default=8001, help="Puerto del Chatbot RAG")
    parser.add_argument("--only", choices=["mcp", "chat", "all"], default="all", help="Que levantar")
    args = parser.parse_args()

    processes = []

    if args.only in ("mcp", "all"):
        print(f"Levantando MCP Server en puerto {args.mcp_port}...")
        p1 = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "src.ts_mcp.server:app",
            "--host", "127.0.0.1",
            "--port", str(args.mcp_port),
        ])
        processes.append(("MCP Server", p1))

    if args.only in ("chat", "all"):
        print(f"Levantando Chatbot RAG en puerto {args.chat_port}...")
        p2 = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "src.ts_chatbot.app:app",
            "--host", "127.0.0.1",
            "--port", str(args.chat_port),
        ])
        processes.append(("Chatbot RAG", p2))

    print("\nServidores iniciados:")
    for name, _ in processes:
        print(f"  - {name}")
    print("\nCtrl+C para detener.\n")

    try:
        for _, p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for _, p in processes:
            p.terminate()
        print("Listo.")


if __name__ == "__main__":
    main()
