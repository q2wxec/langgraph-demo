from typing import Sequence
from langgraph.channels.base import Value

from langgraph.channels.binop import BinaryOperatorAggregate



def update(self, values: Sequence[Value]) -> None:
    if not values:
        return
    if not hasattr(self, "value"):
        self.value = values[0]
        values = values[1:]

    for value in values:
        if isinstance(self.value,list) and not isinstance(value,list):
            value = [value]
        self.value = self.operator(self.value, value)


def mk():
    BinaryOperatorAggregate.update = update