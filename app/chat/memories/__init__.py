from functools import partial
from .sql_memory import build_memory
from .window_memory import window_buffer_memory_builder

memory_map = {
    "sql_buffer_memory": build_memory,
    "sql_window_memory_2": partial(window_buffer_memory_builder, k=2),
    "sql_window_memory_3": partial(window_buffer_memory_builder, k=3)
}