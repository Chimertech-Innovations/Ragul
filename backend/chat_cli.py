import time
from typing import Any, Dict, List
from app.knowledge.rag_engine import rag_engine


def run_cli() -> None:
    history: List[Dict[str, str]] = []
    show_sources: bool = False
    last_sources: List[str] = []

    print("RAGUL Terminal Chat ready.")
    print("Commands: 'show' (toggle sources on/off), 'show last' (print last sources), 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat.")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"exit", "quit", ":q"}:
            print("Goodbye.")
            break

        if cmd in {"show", "show sources", "sources"}:
            show_sources = not show_sources
            state = "ON" if show_sources else "OFF"
            print(f"[Sources display: {state}]")
            if show_sources and last_sources:
                print(f"  Last Sources: {last_sources}")
            continue

        if cmd == "show on":
            show_sources = True
            print("[Sources display: ON]")
            continue

        if cmd == "show off":
            show_sources = False
            print("[Sources display: OFF]")
            continue

        if cmd == "show last":
            print(f"  Last Sources: {last_sources if last_sources else 'None'}")
            continue

        t0 = time.perf_counter()
        result: Dict[str, Any] | None = rag_engine.search(user_input, history=history)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        if not result:
            print("RAGUL: No response returned.")
            continue

        reply = result.get("spoken_response") or result.get("clinical_answer") or ""
        last_sources = result.get("sources") or []
        grounded = result.get("grounded", False)

        print(f"RAGUL ({elapsed_ms:.0f} ms | grounded={grounded}): {reply}")
        if show_sources and last_sources:
            print(f"  Sources: {last_sources}")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    run_cli()
