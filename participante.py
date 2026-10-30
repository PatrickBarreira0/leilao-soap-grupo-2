"""Cliente SOAP gerado dinamicamente a partir do WSDL do Leiloeiro."""

import argparse

from zeep import Client


def main():
    parser = argparse.ArgumentParser(description="Participante do leilão SOAP")
    parser.add_argument("--url", default="http://127.0.0.1:8000/?wsdl")
    sub = parser.add_subparsers(dest="operacao", required=True)
    lance = sub.add_parser("lance", help="Enviar um lance ao Leiloeiro")
    lance.add_argument("nome")
    lance.add_argument("centavos", type=int)
    sub.add_parser("consultar", help="Consultar o estado atual")
    args = parser.parse_args()

    cliente = Client(args.url)
    if args.operacao == "lance":
        resposta = cliente.service.darLance(args.nome, args.centavos)
        print(
            f"aceito={resposta.aceito}; mensagem={resposta.mensagem}; "
            f"maior_lance_centavos={resposta.maior_lance_centavos}; "
            f"lider={resposta.lider or '-'}"
        )
    else:
        estado = cliente.service.consultarLeilao()
        print(
            f"item={estado.descricao}; minimo_centavos={estado.lance_minimo_centavos}; "
            f"maior_lance_centavos={estado.maior_lance_centavos}; "
            f"lider={estado.lider or '-'}; "
            f"segundos_restantes={estado.segundos_restantes}; "
            f"encerrado={estado.encerrado}"
        )


if __name__ == "__main__":
    main()
