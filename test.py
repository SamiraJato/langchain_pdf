from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv
from queue import Queue
from threading import Thread

load_dotenv()

class StreamingHandler(BaseCallbackHandler): # escuta o evento que recebe os blocos de texto vindo do LLM (openai)
    def __init__(self, queue): # construtor
        self.queue = queue
    
    def on_llm_new_token(self, token, **kwargs):
        self.queue.put(token) # lista FIFO
    
    def on_llm_end(self, response, **kwargs):
        self.queue.put(None)

    def on_llm_error(self, error, **kwargs):
        self.queue.put(None)

chat = ChatOpenAI(streaming=True)

prompt = ChatPromptTemplate.from_messages([
    ("human", "{content}")
])


# extendendo a classe LLMChain para implementar a funcionalidade de streaming correta
class StreamableChain: # classe mixin - permite heranca multipla, nao precisa extender todas as classes de chain
    def stream(self, input):
        # isolando contexto do handler e da fila
        queue = Queue()
        handler = StreamingHandler(queue)

        def task(): # definindo funcao para ser executada em thread (tipo lambda do c#)
            self(input, callbacks=[handler]) # referencia para a propria classe, executa como se fosse chain.__call__('dfsdf') ou chain('lkjl')

        Thread(target=task).start() # abre uma thread separada para executar funcao target
       
        # yield retorna um generator para iterar
        while True:
            token = queue.get() # espera aparecer algo na fila e pega o primeiro
            
            if token is None:
                break

            yield token # retorna generator

# define novas classes para extender a mixin + chain especifica
class StreamingChain(StreamableChain, LLMChain):
    pass

chain = StreamingChain(llm=chat, prompt=prompt)

for output in chain.stream(input={"content": "tell me a joke"}):
    print(output)