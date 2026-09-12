"""Contrato de uma fonte e o vocabulário da matriz de cobertura."""
from dataclasses import dataclass, field
from typing import Callable, Literal

# Quanto do alvo no grafo a fonte realmente entrega:
#   real      a fonte pública preenche o campo, com vínculo direto ao cliente
#   parcial   a fonte existe mas não fecha sozinha (nível agregado, match
#             probabilístico, ou campo ausente) — entra com confiança < 1
#   bloqueado a fonte existe, é pública, mas não é consumível por máquina hoje
#             (captcha, chave restrita, URL instável) — precisa de passo manual
#   interno   não existe fonte pública: é dado do ERP da Krilltech
#   sintetico não existe nem fonte pública nem dado interno — precisa ser
#             inventado, e isso tem de estar escrito na tela
Situacao = Literal["real", "parcial", "bloqueado", "interno", "sintetico"]


@dataclass(frozen=True)
class Cobertura:
    """Uma linha da matriz de cobertura: um alvo do grafo e quem o alimenta."""
    alvo: str          # ':Cliente.uf' ou '(:Cliente)-[:TEM_SOCIO]->(:Socio)'
    situacao: Situacao
    confianca: float   # 0..1 — vai gravada na aresta/nó, não é decorativa
    nota: str


@dataclass
class Fonte:
    id: str
    nome: str
    url: str
    orgao: str
    periodicidade: str
    extract: Callable[[], None] | None = None
    transform: Callable[[], None] | None = None
    cobertura: list[Cobertura] = field(default_factory=list)
    # Passo que uma pessoa tem de fazer à mão antes do transform funcionar.
    # Vazio quando a fonte é 100% automatizável.
    passo_manual: str = ""
