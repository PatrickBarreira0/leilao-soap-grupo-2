"""Participante SOAP: lances síncronos e notificações por consulta periódica."""

import argparse
import sys
import threading
import time

from zeep import Client
from zeep.transports import Transport


def criar_cliente(url: str) -> Client:
    # O timeout mantém o processo responsivo quando o Leiloeiro cai.
    return Client(url, transport=Transport(timeout=3, operation_timeout=3))


def mostrar_lance(resposta) -> None:
    print(
        f"aceito={resposta.aceito}; mensagem={resposta.mensagem}; "
        f"maior_lance_centavos={resposta.maior_lance_centavos}; "
        f"lider={resposta.lider or '-'}",
        flush=True,
    )


def mostrar_estado(estado) -> None:
    print(
        f"item={estado.descricao}; minimo_centavos={estado.lance_minimo_centavos}; "
        f"maior_lance_centavos={estado.maior_lance_centavos}; "
        f"lider={estado.lider or '-'}; "
        f"segundos_restantes={estado.segundos_restantes}; "
        f"encerrado={estado.encerrado}",
        flush=True,
    )


def acompanhar(url: str, intervalo: float, parar=None, limite_segundos=None) -> int:
    """Mostra apenas mudanças relevantes; encerra após anunciar o resultado."""
    cliente = None
    ultimo = None
    indisponivel = False
    inicio = time.monotonic()
    while parar is None or not parar.is_set():
        if limite_segundos is not None and time.monotonic() - inicio >= limite_segundos:
            print("Tempo limite de acompanhamento atingido.", flush=True)
            return 2
        try:
            if cliente is None:
                cliente = criar_cliente(url)
            estado = cliente.service.consultarLeilao()
            if indisponivel:
                print("Leiloeiro disponível novamente.", flush=True)
                indisponivel = False
            atual = (estado.descricao, estado.maior_lance_centavos, estado.lider, estado.encerrado)
            if atual != ultimo:
                mostrar_estado(estado)
                if ultimo is not None and not estado.encerrado:
                    print(
                        f"Novo maior lance: {estado.maior_lance_centavos} centavos "
                        f"por {estado.lider or '-'}",
                        flush=True,
                    )
                ultimo = atual
            if estado.encerrado:
                print(
                    f"Leilão encerrado. Vencedor: {estado.lider} "
                    f"com {estado.maior_lance_centavos} centavos."
                    if estado.lider else "Leilão encerrado sem vencedor.",
                    flush=True,
                )
                return 0
        except Exception as erro:
            cliente = None
            if not indisponivel:
                print(f"Leiloeiro indisponível: {erro}", flush=True)
                indisponivel = True
        if parar is not None and parar.wait(intervalo):
            break
        if parar is None:
            time.sleep(intervalo)
    return 0


def participar(url: str, nome: str, intervalo: float) -> int:
    parar = threading.Event()
    observador = threading.Thread(
        target=acompanhar, args=(url, intervalo, parar), daemon=True
    )
    observador.start()
    print(f"Participante {nome}. Digite um lance em centavos ou 'sair'.", flush=True)
    cliente = None
    try:
        while True:
            try:
                linha = input("> ").strip()
            except EOFError:
                break
            if linha.lower() == "sair":
                break
            try:
                valor = int(linha)
            except ValueError:
                print("Digite um valor inteiro em centavos ou 'sair'.", flush=True)
                continue
            try:
                if cliente is None:
                    cliente = criar_cliente(url)
                mostrar_lance(cliente.service.darLance(nome, valor))
            except Exception as erro:
                cliente = None
                print(f"Lance não enviado: {erro}", flush=True)
    except KeyboardInterrupt:
        print("\nParticipante encerrado.", flush=True)
    finally:
        parar.set()
        observador.join(timeout=intervalo + 1)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Participante do leilão SOAP")
    parser.add_argument("--url", default="http://127.0.0.1:8000/?wsdl")
    sub = parser.add_subparsers(dest="operacao", required=True)
    lance = sub.add_parser("lance", help="Enviar um lance ao Leiloeiro")
    lance.add_argument("nome")
    lance.add_argument("centavos", type=int)
    sub.add_parser("consultar", help="Consultar o estado atual")
    monitor = sub.add_parser("acompanhar", help="Observar atualizações até o encerramento")
    monitor.add_argument("--intervalo", type=float, default=1.0)
    monitor.add_argument("--limite-segundos", type=float)
    interativo = sub.add_parser("participar", help="Dar lances e observar atualizações")
    interativo.add_argument("nome")
    interativo.add_argument("--intervalo", type=float, default=1.0)
    args = parser.parse_args()

    if args.operacao in ("acompanhar", "participar") and args.intervalo <= 0:
        parser.error("intervalo deve ser positivo")
    if args.operacao == "acompanhar":
        if args.limite_segundos is not None and args.limite_segundos <= 0:
            parser.error("limite deve ser positivo")
        return acompanhar(args.url, args.intervalo, limite_segundos=args.limite_segundos)
    if args.operacao == "participar":
        return participar(args.url, args.nome, args.intervalo)
    try:
        cliente = criar_cliente(args.url)
        if args.operacao == "lance":
            mostrar_lance(cliente.service.darLance(args.nome, args.centavos))
        else:
            mostrar_estado(cliente.service.consultarLeilao())
        return 0
    except Exception as erro:
        print(f"Erro de comunicação com o Leiloeiro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
