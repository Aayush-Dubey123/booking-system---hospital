import httpx
# pyrefly: ignore [missing-import]
from common.logger import logger

logging = logger(__name__)

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "nomic-embed-text"


async def get_embedding(text: str) -> list[float]:
    """
    Generate vector embedding asynchronously using local Ollama model (nomic-embed-text).
    Tries /api/embed (new API), falls back to /api/embeddings (legacy API).
    Dimension is dynamic based on Ollama model output.
    """
    try:
        logging.info(f"Generating Ollama embedding for text snippet (len: {len(text)})")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "input": text},
            )
            if response.status_code != 200:
                response = await client.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": MODEL_NAME, "prompt": text},
                )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama API returned status {response.status_code}: {response.text}"
            )

        data = response.json()
        embeddings = data.get("embeddings")
        if embeddings and isinstance(embeddings, list) and len(embeddings) > 0:
            vector = embeddings[0]
        else:
            vector = data.get("embedding")

        if not vector or not isinstance(vector, list):
            raise ValueError(f"Invalid embedding returned from Ollama: {data}")

        logging.info(f"Generated embedding of dimension {len(vector)}")
        return vector
    except Exception as error:
        logging.error(f"Error generating embedding with Ollama: {error}")
        raise
