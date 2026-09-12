"""Download das fontes. Cache em disco, retoma de onde parou, falha ruidosa."""
import time
from pathlib import Path

import httpx

from ingestao import config


def baixar(url: str, destino: Path, forcar: bool = False) -> Path:
    """Baixa url para destino, em streaming. Reusa o arquivo se já existir.

    O cache não é otimização: o arquivo da PGFN tem 1,3 GB e o do IBAMA 148 MB.
    Rodar `transform` três vezes enquanto se acerta o parser não pode significar
    baixar 4,5 GB.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0 and not forcar:
        print(f"  cache: {destino.name} ({destino.stat().st_size:,} bytes)")
        return destino

    parcial = destino.with_suffix(destino.suffix + ".parcial")
    cabecalhos = {"User-Agent": config.USER_AGENT}
    with httpx.stream("GET", url, headers=cabecalhos, timeout=config.TIMEOUT,
                      follow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        baixado = 0
        ultimo_log = time.monotonic()
        with parcial.open("wb") as f:
            for bloco in r.iter_bytes(1 << 20):
                f.write(bloco)
                baixado += len(bloco)
                if time.monotonic() - ultimo_log > 5:
                    pct = f" ({100 * baixado // total}%)" if total else ""
                    print(f"  baixando {destino.name}: {baixado:,} bytes{pct}")
                    ultimo_log = time.monotonic()
    # Renomeia só no fim: um .parcial interrompido nunca é confundido com cache
    # válido na próxima execução.
    parcial.replace(destino)
    print(f"  ok: {destino.name} ({destino.stat().st_size:,} bytes)")
    return destino


def json_get(url: str, **kwargs) -> dict | list:
    r = httpx.get(url, headers={"User-Agent": config.USER_AGENT},
                  timeout=config.TIMEOUT, follow_redirects=True, **kwargs)
    r.raise_for_status()
    return r.json()


def json_post(url: str, payload: dict, cabecalhos: dict | None = None) -> dict:
    h = {"User-Agent": config.USER_AGENT, "Content-Type": "application/json"}
    h.update(cabecalhos or {})
    r = httpx.post(url, json=payload, headers=h, timeout=config.TIMEOUT,
                   follow_redirects=True)
    r.raise_for_status()
    return r.json()
