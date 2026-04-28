"""
Runner de smoke tests — ejecuta los 7 tests en orden, mide tiempos y reporta.

Salida en formato compacto + tabla resumen al final. Termina con exit code 0
si los 7 pasan, 1 en caso contrario.

Uso:
    pip install -r requirements.txt
    python run_all.py
"""

from __future__ import annotations

import importlib
import sys
import time
from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    ok: bool
    message: str
    elapsed_s: float


TESTS = [
    "test_01_postgres",
    "test_02_mongo",
    "test_03_rabbitmq_basic",
    "test_04_delayed_exchange",
    "test_05_dlx",
    "test_06_request_reply",
    "test_07_outbox",
]


def run_one(module_name: str) -> TestResult:
    started = time.time()
    try:
        mod = importlib.import_module(module_name)
        ok, msg = mod.run()
    except Exception as exc:  # noqa: BLE001
        ok = False
        msg = f"crash: {type(exc).__name__}: {exc}"
    elapsed = time.time() - started
    return TestResult(name=module_name, ok=ok, message=msg, elapsed_s=elapsed)


def render_summary(results: list[TestResult]) -> None:
    print()
    print("=" * 72)
    print(f"{'Test':<28} {'Estado':<8} {'Tiempo':>10}  Detalle")
    print("-" * 72)
    for r in results:
        status = "OK" if r.ok else "FAIL"
        print(f"{r.name:<28} {status:<8} {r.elapsed_s:>8.2f}s  {r.message}")
    print("=" * 72)
    passed = sum(1 for r in results if r.ok)
    total = len(results)
    overall = "OK" if passed == total else "FAIL"
    print(f"Resultado: {passed}/{total} {overall}")
    print("=" * 72)


def main() -> int:
    print("Sistema de Pañol — smoke tests de infraestructura")
    print(f"Ejecutando {len(TESTS)} tests…")
    print()

    results: list[TestResult] = []
    for test in TESTS:
        print(f"  → corriendo {test}…", end=" ", flush=True)
        r = run_one(test)
        marker = "OK" if r.ok else "FAIL"
        print(f"{marker} ({r.elapsed_s:.2f}s)")
        if not r.ok:
            print(f"      {r.message}")
        results.append(r)

    render_summary(results)
    return 0 if all(r.ok for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
