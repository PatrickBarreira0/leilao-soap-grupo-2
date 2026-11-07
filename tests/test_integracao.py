"""Experimentos reais com servidor e clientes SOAP em processos distintos."""

import socket
import subprocess
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen


RAIZ = Path(__file__).resolve().parents[1]


def porta_livre():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def iniciar_servidor(porta, duracao):
    processo = subprocess.Popen(
        [
            sys.executable,
            "leiloeiro.py",
            "--porta", str(porta),
            "--duracao-segundos", str(duracao),
        ],
        cwd=RAIZ,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if processo.poll() is not None:
            raise RuntimeError(f"Leiloeiro terminou com código {processo.returncode}")
        try:
            with urlopen(f"http://127.0.0.1:{porta}/?wsdl", timeout=1) as resposta:
                assert b"darLance" in resposta.read()
            return processo
        except Exception:
            time.sleep(0.05)
    processo.terminate()
    raise RuntimeError("WSDL não ficou disponível")


def parar_servidor(processo):
    if processo.poll() is None:
        processo.terminate()
        processo.wait(timeout=10)


def cliente(porta, *argumentos):
    return subprocess.run(
        [
            sys.executable,
            "participante.py",
            "--url", f"http://127.0.0.1:{porta}/?wsdl",
            *argumentos,
        ],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )


class IntegracaoSOAP(unittest.TestCase):
    def test_lances_polling_encerramento(self):
        porta = porta_livre()
        servidor = iniciar_servidor(porta, 5)
        url = f"http://127.0.0.1:{porta}/?wsdl"
        observadores = [
            subprocess.Popen(
                [sys.executable, "participante.py", "--url", url,
                 "acompanhar", "--intervalo", "0.2", "--limite-segundos", "10"],
                cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8",
            )
            for _ in range(2)
        ]
        try:
            time.sleep(1)
            self.assertIn("aceito=True", cliente(porta, "lance", "Ana", "1500").stdout)
            time.sleep(0.6)
            self.assertIn("aceito=True", cliente(porta, "lance", "Bruno", "2000").stdout)
            saidas = []
            for observador in observadores:
                saida, erro = observador.communicate(timeout=10)
                self.assertEqual(observador.returncode, 0, erro)
                self.assertIn("Novo maior lance: 1500", saida)
                self.assertIn("Novo maior lance: 2000", saida)
                self.assertIn("Vencedor: Bruno com 2000 centavos", saida)
                saidas.append(saida)
            tardio = cliente(porta, "lance", "Ana", "3000")
            self.assertEqual(tardio.returncode, 0, tardio.stderr)
            self.assertIn("aceito=False", tardio.stdout)
            self.assertIn("Leilão encerrado", tardio.stdout)
            print("Polling: dois observadores viram 1500, 2000 e vencedor Bruno")
            print("Após encerramento: lance 3000 recusado")
        finally:
            for observador in observadores:
                if observador.poll() is None:
                    observador.terminate()
                    observador.wait(timeout=5)
            parar_servidor(servidor)

    def test_falha_e_reinicio(self):
        porta = porta_livre()
        servidor = iniciar_servidor(porta, 30)
        try:
            self.assertIn("aceito=True", cliente(porta, "lance", "Ana", "1500").stdout)
            parar_servidor(servidor)
            falha = cliente(porta, "consultar")
            self.assertEqual(falha.returncode, 1)
            self.assertIn("Erro de comunicação", falha.stderr)
            servidor = iniciar_servidor(porta, 30)
            estado = cliente(porta, "consultar")
            self.assertEqual(estado.returncode, 0, estado.stderr)
            self.assertIn("maior_lance_centavos=0", estado.stdout)
            print("Falha: cliente reportou indisponibilidade; reinício zerou estado")
        finally:
            parar_servidor(servidor)

    def test_concorrencia_mesmo_valor(self):
        porta = porta_livre()
        servidor = iniciar_servidor(porta, 30)
        barreira = threading.Barrier(2)

        def enviar(nome):
            barreira.wait(timeout=5)
            return cliente(porta, "lance", nome, "1500")

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futuros = [executor.submit(enviar, nome) for nome in ("Ana", "Bruno")]
                respostas = [f.result(timeout=20) for f in futuros]
            self.assertTrue(all(r.returncode == 0 for r in respostas))
            self.assertEqual(sum("aceito=True" in r.stdout for r in respostas), 1)
            self.assertEqual(sum("aceito=False" in r.stdout for r in respostas), 1)
            estado = cliente(porta, "consultar")
            self.assertIn("maior_lance_centavos=1500", estado.stdout)
            print("Concorrência:", " | ".join(r.stdout.strip() for r in respostas))
        finally:
            parar_servidor(servidor)


if __name__ == "__main__":
    unittest.main(verbosity=2)
