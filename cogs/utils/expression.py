import asyncio
from py_expression_eval import Parser


def parse_expression(expression):
    if len(expression) > 500:
        raise ValueError("Expression is too long.")
    return Parser().parse(expression.replace("x", "*").replace(":", "/")).evaluate({})


async def evaluate(expression):
    return await asyncio.wait_for(asyncio.to_thread(parse_expression, expression), timeout=1)
