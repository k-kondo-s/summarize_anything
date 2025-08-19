FROM python:3.11

# FFmpegのインストール
RUN apt-get update && apt-get install -y ffmpeg

# Poetryのインストール
RUN pip install poetry

# ワークディレクトリの設定
WORKDIR /app

# Poetryの設定ファイルをコピー
COPY pyproject.toml poetry.lock ./

# Poetryの環境設定
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 依存関係のインストール
RUN poetry install --no-interaction --no-ansi --no-root && rm -rf $POETRY_CACHE_DIR

# アプリケーションのソースコードをコピー
COPY . .

# コンテナ起動時に実行するコマンド
CMD ["python", "discord_launcher.py"]
