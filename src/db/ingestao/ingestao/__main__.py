"""CLI do pipeline.  python -m ingestao <comando> [--fonte id ...]

  extract    baixa o bruto das fontes para data/raw/
  transform  normaliza para data/staging/
  load       MERGE no Neo4j (precisa de credencial no .env)
  all        extract + transform + load
  cobertura  regenera COBERTURA.md a partir das declarações das fontes
  fontes     lista as fontes e o que cada uma automatiza
"""
import argparse
import sys

from ingestao import config
from ingestao.registry import FONTES, resolver


def _rodar(etapa: str, fontes) -> None:
    for f in fontes:
        funcao = getattr(f, etapa)
        if funcao is None:
            print(f"\n== {f.id}: sem {etapa} (fonte declarada, nao automatizada)")
            if f.passo_manual:
                print(f"   passo manual: {f.passo_manual}")
            continue
        print(f"\n== {f.id} · {etapa} · {f.nome}")
        funcao()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ingestao", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("comando", choices=[
        "extract", "transform", "load", "all", "cobertura", "fontes"])
    p.add_argument("--fonte", action="append", metavar="ID",
                   help="limita a uma fonte (repetível). Padrão: todas.")
    args = p.parse_args(argv)

    if args.comando == "fontes":
        for f in FONTES:
            automacao = ("extract+transform" if f.extract and f.transform
                         else "declaracao")
            print(f"  {f.id:<14} {automacao:<18} {f.nome}")
            if f.passo_manual:
                print(f"  {'':<14} manual: {f.passo_manual}")
        return 0

    if args.comando == "cobertura":
        from ingestao import cobertura
        cobertura.escrever()
        return 0

    config.preparar_diretorios()
    fontes = resolver(args.fonte)

    if args.comando in ("extract", "all"):
        _rodar("extract", fontes)
    if args.comando in ("transform", "all"):
        _rodar("transform", fontes)
    if args.comando in ("load", "all"):
        # O load é único para todas as fontes: ele lê o staging inteiro, não
        # fonte por fonte. Carregar "só o PGFN" deixaria o grafo num estado
        # meio-carregado que o motor leria como carteira completa.
        print("\n== load · staging -> Neo4j")
        from ingestao.carga import loader
        loader.rodar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
