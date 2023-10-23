from pathlib import Path


def get_directory_files(path: Path):
    paths = [path]
    for path in paths:
        if path.is_dir():
            paths.extend(path for path in path.iterdir())
        elif path.is_file():
            yield path


if __name__ == "__main__":
    for path in get_directory_files(Path(".")):
        print(path)
