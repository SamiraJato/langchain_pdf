from functools import partial
from .chatopenai import build_llm

llm_map = {
    "gpt-4": partial(build_llm, model_name="gpt-4"), # adianta a passagem do paramentro de model, ja deixa pre definido
    "gpt-3.5-turbo": partial(build_llm, model_name="gpt-3.5-turbo")
}

# USO:
# builder = llm_map["gpt-4"]
# builder(chat_args)