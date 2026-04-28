"""
Smoke test 02 — MongoDB.

Valida:
  - Conexión con las credenciales del .env.
  - Insert + find + update + delete sobre una colección.
  - Índice único sobre `sku` para prevenir duplicados (analogía con catálogo de
    inventario en producción).

Mapea a: persistencia del catálogo de inventario (inventory-svc → MongoDB,
ADR-002 polyglot persistence).
"""

from __future__ import annotations

import sys

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import config


TEST_NAME = "test_02_mongo"
DB_NAME = "smoke_catalog"
COLLECTION = "resources"


def run() -> tuple[bool, str]:
    try:
        client = MongoClient(config.mongo_uri(), serverSelectionTimeoutMS=5000)
        client.server_info()  # forzar conexión

        db = client[DB_NAME]
        col = db[COLLECTION]
        col.drop()  # estado limpio

        # Índice único sobre sku
        col.create_index("sku", unique=True, name="ux_sku")

        # Insert
        result = col.insert_one(
            {
                "sku": "MART-001",
                "name": "Martillo de carpintero",
                "category": "herramientas",
                "active": True,
            }
        )
        assert result.inserted_id is not None, "inserted_id debería estar definido"

        # Find
        doc = col.find_one({"sku": "MART-001"})
        assert doc is not None, "documento no encontrado tras insert"
        assert doc["name"] == "Martillo de carpintero"

        # Update
        col.update_one({"sku": "MART-001"}, {"$set": {"active": False}})
        doc = col.find_one({"sku": "MART-001"})
        assert doc["active"] is False

        # Restricción de unicidad
        try:
            col.insert_one({"sku": "MART-001", "name": "duplicado"})
            return False, "se esperaba DuplicateKeyError pero no ocurrió"
        except DuplicateKeyError:
            pass  # esperado

        # Delete + cleanup
        col.delete_many({})
        assert col.count_documents({}) == 0
        client.drop_database(DB_NAME)
        client.close()

        return True, "insert/find/update OK, índice único OK, cleanup OK"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
