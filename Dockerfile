FROM python:3.11

# FFmpegのインストール
RUN apt-get update && apt-get install -y ffmpeg

# Poetryのインストール
RUN pip install poetry

# ワークディレクトリの設定
WORKDIR /app

# Poetryの設定ファイルをコピー
COPY pyproject.toml poetry.lock ./

# 依存関係のインストール
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# アプリケーションのソースコードをコピー
COPY . .

# コンテナ起動時に実行するコマンド
CMD ["python", "discord_launcher.py"]
