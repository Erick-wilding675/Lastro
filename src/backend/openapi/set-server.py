"""Preenche o bloco servers dos specs do Lastro com a URL publica do backend.

Uso:  python set-server.py https://sua-url-publica.trycloudflare.com
"""
import json
import pathlib
import sys

if len(sys.argv) != 2:
    sys.exit("uso: python set-server.py https://sua-url-publica")

url = sys.argv[1].rstrip("/")
if not url.startswith("https://"):
    sys.exit("a URL precisa ser https — o Orchestrate nao chama http nem localhost")

aqui = pathlib.Path(__file__).parent
for spec in sorted(aqui.glob("*.openapi.json")):
    doc = json.loads(spec.read_text(encoding="utf-8"))
    doc["servers"] = [{"url": url}]
    spec.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ok  {spec.name}  ->  {url}")
