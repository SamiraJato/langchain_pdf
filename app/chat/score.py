import random
from app.chat.redis import client

def random_component_by_score(component_type, component_map):
    # verifica component_type
    if component_type not in ["llm", "retriever", "memory"]:
        raise ValueError("Invalid component_type")
    
    # pega os scores daquele component_type no redis
    values = client.hgetall(f"{component_type}_score_values") # pega todos os key:value pairs dentro de uma "tabela" ex: llm_score_values
    # pega as qtds de score daquele component_type no redis
    counts = client.hgetall(f"{component_type}_score_counts")

    # pega todos os nomes de componente validos
    names = component_map.keys()

    # itera em todos os componentes e calcula a media de score e coloca em dicionario
    avg_scores = {}
    for name in names:
        score = int(values.get(name, 1)) # busca o score daquele nome de componente (se nao tiver, retorna default 1 para nao atrapalhar a media)
        count = int(counts.get(name, 1))
        avg = score / count 
        avg_scores[name] = max(avg, 0.1) # garante que nunca vai ficar zerado, se o primeiro voto for 0 pode zerar o componente pra sempre (nunca mais sera selecionado)

    # seleciona o componente randomico com peso no score
    # score eh uma chance proporcional de ser selecionado
    sum_scores = sum(avg_scores.values())
    random_val = random.uniform(0, sum_scores)
    cumulative = 0
    for name, score in avg_scores.items():
        cumulative += score
        if random_val <= cumulative:
            return name


def score_conversation(
    conversation_id: str, score: float, llm: str, retriever: str, memory: str
) -> None:
    """
    This function interfaces with langfuse to assign a score to a conversation, specified by its ID.
    It creates a new langfuse score utilizing the provided llm, retriever, and memory components.
    The details are encapsulated in JSON format and submitted along with the conversation_id and the score.

    :param conversation_id: The unique identifier for the conversation to be scored.
    :param score: The score assigned to the conversation.
    :param llm: The Language Model component information.
    :param retriever: The Retriever component information.
    :param memory: The Memory component information.

    Example Usage:

    score_conversation('abc123', 1, 'llm_info', 'retriever_info', 'memory_info')
    """

    score = min(max(score,0), 1) # normalizar entrada

    # atualiza no redis todos os scores de cada componente
    client.hincrby("llm_score_values", llm, score) # incrementa uma chave dentro de um hash pelo score/amount
    client.hincrby("llm_score_counts", llm, 1)

    client.hincrby("retriever_score_values", retriever, score) 
    client.hincrby("retriever_score_counts", retriever, 1)

    client.hincrby("memory_score_values", memory, score)
    client.hincrby("memory_score_counts", memory, 1)


def get_scores():
    """
    Retrieves and organizes scores from the langfuse client for different component types and names.
    The scores are categorized and aggregated in a nested dictionary format where the outer key represents
    the component type and the inner key represents the component name, with each score listed in an array.

    The function accesses the langfuse client's score endpoint to obtain scores.
    If the score name cannot be parsed into JSON, it is skipped.

    :return: A dictionary organized by component type and name, containing arrays of scores.

    Example:

        {
            'llm': {
                'chatopenai-3.5-turbo': [avg_score],
                'chatopenai-4': [avg_score]
            },
            'retriever': { 'pinecone_store': [avg_score] },
            'memory': { 'persist_memory': [avg_score] }
        }
    """

    aggregate = {"llm": {}, "retriever": {}, "memory": {}}

    # calculando a media de score de cada tipo de componente
    for component_type in aggregate.keys():
        values = client.hgetall(f"{component_type}_score_values")
        counts = client.hgetall(f"{component_type}_score_counts")

        names = values.keys()

        for name in names:
            score = int(values.get(name, 1))
            count = int(counts.get(name, 1))
            avg = score / count
            aggregate[component_type][name] = [avg]


    return aggregate