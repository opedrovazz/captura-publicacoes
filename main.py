import sys
import threading
from api import create_app
from scheduler import start_scheduler, run_all_scrapers


def start_api():
    """Inicializa o servidor Flask."""
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)


def start_scheduler_thread():
    """Inicia o scheduler em uma thread separada."""
    try:
        run_all_scrapers()
        start_scheduler()
    except KeyboardInterrupt:
        print("Encerrando scheduler...")


def main():
    """
    Ponto de entrada principal.

    Modos de execução:
      python main.py api        → Inicia apenas a API
      python main.py scheduler  → Inicia apenas o scheduler
      python main.py both       → Inicia API e scheduler simultaneamente
    """
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py api        → Inicia o servidor Flask")
        print("  python main.py scheduler  → Inicia o agendador diário")
        print("  python main.py both       → Inicia ambos simultaneamente")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "api":
        start_api()

    elif command == "scheduler":
        start_scheduler_thread()

    elif command == "both":
        # API em uma thread separada
        api_thread = threading.Thread(target=start_api, daemon=True)
        api_thread.start()

        # Scheduler na thread principal
        start_scheduler_thread()

    else:
        print(f"Comando inválido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
