import inspect
from . import methods
from .definition import theClass

for name, f in methods.__dict__.items():
    if not callable(f):
        continue
    args = list(inspect.signature(f).parameters.keys())
    if len(args) and args[0] == 'self':
        setattr(theClass, name, f)
