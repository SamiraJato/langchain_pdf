from flask import current_app
from queue import Queue
from threading import Thread

from app.chat.callbacks.stream import StreamingHandler
 

# extendendo a classe LLMChain para implementar a funcionalidade de streaming correta
class StreamableChain: # classe mixin - permite heranca multipla, nao precisa extender todas as classes de chain
    def stream(self, input):
        # isolando contexto do handler e da fila
        queue = Queue()
        handler = StreamingHandler(queue)

        def task(app_context): # definindo funcao para ser executada em thread (tipo lambda do c#)
            app_context.push() # necessario por causa do Flask, precisa incluir o contexto do app na nova thread
            self(input, callbacks=[handler]) # referencia para a propria classe, executa como se fosse chain.__call__('dfsdf') ou chain('lkjl')

        Thread(target=task, args=[current_app.app_context()]).start() # abre uma thread separada para executar funcao target
       
        # yield retorna um generator para iterar
        while True:
            token = queue.get() # espera aparecer algo na fila e pega o primeiro
            
            if token is None:
                break

            yield token # retorna generator