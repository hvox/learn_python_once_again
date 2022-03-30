def hi():
    """this very useful function does very hard job of printing "hi"

    >>> hi()
    hi
    """
    print("hi")


if __name__ == "__main__":
    import doctest
    doctest.testmod()
