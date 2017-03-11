import random
from .exception import ParseError


def random_string(alphabet, length):
    result = ""
    for i in range(length):
        result += random.choice(alphabet)
    return result


def arguments(*arg_types):
    types = {len(pair): pair for pair in arg_types}

    def decorator(func):
        def wrapper(update, args, **kwargs):
            if len(args) not in types:
                raise ParseError("Not enough or too many arguments")
            parsed = []
            for i in range(len(args)):
                try:
                    if types[len(args)][i]:
                        parsed.append(types[len(args)][i](args[i]))
                    else:
                        parsed.append(args[i])
                except:
                    raise ParseError(str(args[i]))
            return func(update, tuple(parsed), **kwargs)
        return wrapper
    return decorator
