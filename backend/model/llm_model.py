# import httpx
from langchain_openai import ChatOpenAI
from env_utils import LLM_API_KEY, LLM_MODEL_NAME, LLM_MODEL_URL

# HTTP_CLIENT = httpx.Client(trust_env=False)

actor_openai_llm = ChatOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_MODEL_URL,
    model=LLM_MODEL_NAME,
    temperature=0.7,
    timeout=10000,
    # http_client=HTTP_CLIENT,
)


Evaluator_openai_llm = ChatOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_MODEL_URL,
    model=LLM_MODEL_NAME,
    temperature=0.2,
    timeout=10000,
    # http_client=HTTP_CLIENT,
)
