python_eval = eval


def eval(vars: dict[str, str]):
    vars = dict(vars)
    dependencies = {}
    resolved_vars = {}
    while vars:
        for name, expr in list(vars.items()):
            try:
                value = python_eval(expr, dict(resolved_vars))
                resolved_vars[name] = value
                vars.pop(name)
            except NameError as error:
                dependancy = error.args[0].split("'")[1]
                dependencies[name] = dependancy
        if vars and not set(dependencies.values()) & set(resolved_vars):
            raise RecursionError("Infinite cycle: TODO")
    return resolved_vars


def get_cycle(graph: dict[str, str]) -> list[str]:
    raise NotADirectoryError()


vars = {
    "x": "y * z",
    "y": "123 + z",
    "z": "321",
}
print(eval(vars))
