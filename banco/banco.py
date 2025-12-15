import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "cancela.db")

TIPOS_VALIDOS = {"ENTRADA", "SAIDA", "NEGADO"}


class BancoDeDados:
    def __init__(self, db_name: str = DB_PATH):
        self.db_name = db_name
        self._criar_tabelas()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def _criar_tabelas(self):
        conn = self.conectar()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS placas_autorizadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            descricao TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS movimentacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            tipo TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_movimento_placa
        ON movimentacao (placa);
        """)

        conn.commit()
        conn.close()

    def adicionar_placa(self, placa: str, descricao: str = "") -> bool:
        placa = self._normalize_plate(placa)
        if not placa:
            return False

        conn = self.conectar()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO placas_autorizadas (placa, descricao) VALUES (?, ?)",
                (placa, descricao)
            )
            conn.commit()
            return True

        except sqlite3.IntegrityError:
            return False

        finally:
            conn.close()

    def listar_placas(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("SELECT placa, descricao FROM placas_autorizadas")
        dados = cur.fetchall()
        conn.close()
        return dados

    def remover_placa(self, placa: str) -> bool:
        placa = self._normalize_plate(placa)

        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM placas_autorizadas WHERE placa = ?", (placa,)
        )
        afetadas = cur.rowcount
        conn.commit()
        conn.close()

        return afetadas > 0

    def placa_autorizada(self, placa: str) -> bool:
        placa = self._normalize_plate(placa)

        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM placas_autorizadas WHERE placa = ? LIMIT 1",
            (placa,)
        )
        found = cur.fetchone() is not None
        conn.close()
        return found

    def registrar_movimento(self, placa: str, tipo: str):
        tipo = tipo.upper()
        if tipo not in TIPOS_VALIDOS:
            raise ValueError("Tipo inválido")

        placa = self._normalize_plate(placa)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO movimentacao (placa, data_hora, tipo) VALUES (?, ?, ?)",
            (placa, agora, tipo)
        )
        conn.commit()
        conn.close()

    def esta_no_patio(self, placa: str) -> bool:
        placa = self._normalize_plate(placa)

        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT tipo FROM movimentacao WHERE placa = ? ORDER BY id DESC LIMIT 1",
            (placa,)
        )
        linha = cur.fetchone()
        conn.close()

        return linha and linha[0] == "ENTRADA"

    def listar_movimentacao(self) -> List[Tuple]:
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT placa, data_hora, tipo FROM movimentacao ORDER BY id DESC"
        )
        dados = cur.fetchall()
        conn.close()
        return dados

    def get_last_movimento(self, placa: str):
        placa = self._normalize_plate(placa)
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute(
            "SELECT data_hora, tipo FROM movimentacao WHERE placa = ? ORDER BY id DESC LIMIT 1",
            (placa,)
        )
        row = cur.fetchone()
        conn.close()
        return row


    @staticmethod
    def _normalize_plate(plate: Optional[str]) -> str:
        if not plate:
            return ""
        return "".join(c for c in plate.upper() if c.isalnum())
