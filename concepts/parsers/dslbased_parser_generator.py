import inspect


def lazy_function(function_generator):
    def f(*args, **kwargs):
        nonlocal f
        f = function_generator()
        return f(*args, **kwargs)
    return lambda *args, **kwargs: f(*args, **kwargs)


def parse_ebnf_nonterminal(source, i=0):
    j = i
    while i < len(source) and source[i] not in ",|":
        i += 1
    return source[j:i].strip(), i


def parse_ebnf_expression(source, i=0):
    nonterm, i = parse_ebnf_nonterminal(source, i)
    clauses = [[nonterm]]
    while i < len(source):
        match source[i]:
            case ",":
                nonterm, i = parse_ebnf_nonterminal(source, i + 1)
                clauses.append([nonterm])
            case "|":
                nonterm, i = parse_ebnf_nonterminal(source, i + 1)
                clauses[-1].append(nonterm)
    clauses = [cls[0] if len(cls) == 1 else ("or", *cls) for cls in clauses]
    return ("and", *clauses)
    return clauses[0] if len(clauses) == 1 else ("and", *clauses)


def concatenate(parsers):
    def parse(source, i=0):
        results = []
        for parser in parsers:
            match parser(source, i):
                case None:
                    return None
                case result, i:
                    results.append(result)
        return results, i
    parse.is_concatenation = True
    return parse


def alternate(parsers):
    def parse(source, i=0):
        for parser in parsers:
            match parser(source, i):
                case result, i:
                    return result, i
        return None
    return parse


class ParserGenerator:
    def __init__(self, namespace=None):
        if namespace is None:
            namespace = inspect.getmodule(inspect.stack()[1][0])
        self.namespace = namespace

    def __call__(self, grammar, postprocessing=None):
        if postprocessing is None:
            return lambda postprocessing: self(grammar, postprocessing)
        parser = self.build_parser(parse_ebnf_expression(grammar))

        def parse(source, i=0):
            match parser(source, i):
                case None:
                    return None
                case parsed, j:
                    print("parsed", repr(parsed))
                    return postprocessing((i, j), *parsed)
        return parse

    def __getitem__(self, nonterminal):
        parser_name = "parse_" + nonterminal
        return lazy_function(lambda: getattr(self.namespace, parser_name))

    def build_parser(self, ebnf):
        match ebnf:
            case str(nonterminal):
                return self[nonterminal]
            case "and", *parsers:
                return concatenate([self.build_parser(p) for p in parsers])
            case "or", *parsers:
                return alternate([self.build_parser(p) for p in parsers])


parser = ParserGenerator()
LETTERS = "qfuyzxkcwboheaidrtnsmjglpv"


def parse_whitespaces(source, i=0):
    j = i
    while i < len(source) and source[i] in " \t\n":
        i += 1
    return source[j:i], i


def parse_comment(source, i=0):
    if source[i] != "#":
        return None
    j, i = i, i + 1
    while i < len(source) and source[i - 1] != "\n":
        i += 1
    return source[j + 1: i], i


def parse_word(source, i=0):
    if source[i] not in LETTERS:
        return None
    j = i
    while i < len(source) and source[i] in LETTERS:
        i += 1
    return source[j:i], i


@parser("comment | whitespaces , word , whitespaces")
def parse_identifier(span, _, word, __):
    return ("id", *span, word)

print(parse_identifier("#hea\nohntoorntr   "))
