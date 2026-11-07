"""Protótipo do Leiloeiro: serviço SOAP 1.1 com contrato WSDL 1.1."""

import argparse
from datetime import datetime, timedelta, timezone
from socketserver import ThreadingMixIn
from threading import Lock
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server

from spyne import Application, Boolean, ComplexModel, Integer, ServiceBase, Unicode, rpc
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class RespostaLance(ComplexModel):
    aceito = Boolean
    mensagem = Unicode
    maior_lance_centavos = Integer
    lider = Unicode


class EstadoLeilao(ComplexModel):
    descricao = Unicode
    lance_minimo_centavos = Integer
    maior_lance_centavos = Integer
    lider = Unicode
    segundos_restantes = Integer
    encerrado = Boolean


class Leilao:
    def __init__(self, descricao: str, minimo: int, duracao: int):
        self.descricao = descricao
        self.minimo = minimo
        self.fim = datetime.now(timezone.utc) + timedelta(seconds=duracao)
        self.maior = 0
        self.lider = ""
        self.lock = Lock()

    def segundos_restantes(self) -> int:
        return max(0, int((self.fim - datetime.now(timezone.utc)).total_seconds()))


leilao: Leilao


class ServicoLeilao(ServiceBase):
    @rpc(Unicode, Integer, _returns=RespostaLance)
    def darLance(ctx, participante, valor_centavos):
        with leilao.lock:
            if datetime.now(timezone.utc) >= leilao.fim:
                mensagem = "Leilão encerrado"
            elif not participante or not participante.strip():
                mensagem = "Informe o participante"
            elif valor_centavos < leilao.minimo:
                mensagem = "Lance abaixo do mínimo"
            elif valor_centavos <= leilao.maior:
                mensagem = "Lance não supera o maior atual"
            else:
                leilao.maior = valor_centavos
                leilao.lider = participante.strip()
                return RespostaLance(
                    aceito=True,
                    mensagem="Lance aceito",
                    maior_lance_centavos=leilao.maior,
                    lider=leilao.lider,
                )
            return RespostaLance(
                aceito=False,
                mensagem=mensagem,
                maior_lance_centavos=leilao.maior,
                lider=leilao.lider,
            )

    @rpc(_returns=EstadoLeilao)
    def consultarLeilao(ctx):
        with leilao.lock:
            return EstadoLeilao(
                descricao=leilao.descricao,
                lance_minimo_centavos=leilao.minimo,
                maior_lance_centavos=leilao.maior,
                lider=leilao.lider,
                segundos_restantes=leilao.segundos_restantes(),
                encerrado=datetime.now(timezone.utc) >= leilao.fim,
            )


class ServidorConcorrente(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Leiloeiro SOAP do grupo 2")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--descricao", default="Livro de sistemas distribuídos")
    parser.add_argument("--minimo-centavos", type=int, default=1000)
    parser.add_argument("--duracao-segundos", type=int, default=300)
    args = parser.parse_args()
    if args.minimo_centavos <= 0 or args.duracao_segundos <= 0:
        parser.error("mínimo e duração devem ser positivos")

    global leilao
    leilao = Leilao(args.descricao, args.minimo_centavos, args.duracao_segundos)
    app = Application(
        [ServicoLeilao],
        tns="urn:grupo2:leilao:soap",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )
    servidor = make_server(
        args.host,
        args.porta,
        WsgiApplication(app),
        server_class=ServidorConcorrente,
        handler_class=WSGIRequestHandler,
    )
    print(f"Leiloeiro em http://{args.host}:{args.porta}/?wsdl", flush=True)
    print("Estado em memória; reiniciar o servidor reinicia o leilão.", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Leiloeiro encerrado.", flush=True)
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
