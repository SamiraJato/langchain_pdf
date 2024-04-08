from langfuse.model import CreateTrace
from app.chat.tracing.langfuse import langfuse

class TraceableChain:
    def __call__(self, *args, **kwargs):
        trace = langfuse.trace(
                        CreateTrace(
                            id=self.metadata["conversation_id"], # define um agrupamento de trace
                            metadata=self.metadata
                        )
                    )
        
        # adiciona automaticamente o callback do trace na chamada da chain
        callbacks = kwargs.get("callbacks", []) # tenta pegar a lista existente de callbacks
        callbacks.append(trace.getNewHandler())
        kwargs["callbacks"] = callbacks

        return super().__call__(*args, **kwargs)