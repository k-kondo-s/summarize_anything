# Summarize Anything


## 実行 routine

build & push

```
docker build --no-cache --tag kenchaaan/summarize_anything:v1 .
docker push kenchaaan/summarize_anything:v1
```

```
docker stop summarizer
docker rm summarizer
docker pull kenchaaan/summarize_anything:v1
docker run -d --name summarizer --platform=linux/arm64/v8 --env-file ~/work/codes/summarize_anything_server/.env  kenchaaan/summarize_anything:v1
```

ちなみに、中の様子をみる

```
docker exec -it summarizer /bin/sh
```

A Discord bot that summarizes texts, articles on the Internet, YouTube movies and papers on arXiv and so on, using the [Langchain API](https://langchain.com/).

## Quickstart

0. ffmpeg をインストールしといて

1. Clone the repository:

   ```bash
   git clone https://github.com/k-kondo-s/summarize_anything
   ```

2. Install the dependencies:

   This project uses Poetry for dependency management. If you haven't installed it yet, you can do so by following the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).

   Once Poetry is installed, navigate to the project directory and run:

   ```bash
   poetry install
   ```

3. Set up the environment variables:

   Copy the `.env` file to `.env.local` and fill in the necessary details. The `.env` file contains the following variables:

   ```env
   DISCORD_BOT_TOKEN=""
   DISCORD_ALLOWED_CHANNEL_ID_LIST="" # comma separated list of channel ID
   OPENAI_API_KEY=""
   ANTHROPIC_API_KEY=""
   LANGCHAIN_TRACING_V2=""
   LANGCHAIN_API_KEY=""
   ```

4. Run the bot:

```bash
python discord_launcher.py
```

## Development

1. Install the development dependencies:

   ```bash
   poetry install --dev
   ```

2. Run the tests:

   This project uses pytest for testing. You can run the tests with the following command:

   ```bash
   pytest
   ```

3. Linting and formatting:

Using ruff.
