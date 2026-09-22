FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 AUTHORITY_DB=/data/authority.db
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 authority
USER authority
VOLUME ["/data"]
EXPOSE 8765
ENTRYPOINT ["authority","control","--host","0.0.0.0","--port","8765"]
