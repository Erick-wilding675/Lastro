# Imagem do backend do Lastro. 3.11 e não 3.14: pydantic-core ainda não publica
# wheel para 3.14 e a build cai no cargo/PyO3.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# A porta vem do ambiente: Render, Railway e Fly injetam $PORT e ignoram
# qualquer porta fixa que a aplicação escolha.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
