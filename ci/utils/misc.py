import os
import json

from pathlib import Path


def find_repo_path(path: str = __file__) -> str:
    """Find the root path of the repository and return it.
    :param path: The path where we should be looking.
    :return: The root path of the repository.
    :rtype: str
    """
    for path in Path(path).parents:
        # Check whether "path/.git" exists and is a directory
        git_dir = path / ".git"
        if git_dir.is_dir():
            return path.as_posix()


def get_tf_dirs(path: str, file_ext: str = ".tf") -> list:
    """Get a list of terraform project directories in this repository.
    :param path: The path to search.
    :param file_ext: The file extension to search for. Generally this is left at .tf.
    :return: A list of directories that only contain the specified file exstension.
    :rtype: list[str]
    """
    # a list of strings we want to avoid when searching for terraform directories
    EXCLUDED_STR = [".terraform"]
    dirs = []

    # return nothing if path is a file
    if os.path.isfile(path):
        return []

    # add dir to dirs if it contains .tf files
    if len([f for f in os.listdir(path) if f.endswith(file_ext)]) > 0:
        # we dont want to include the excluded dirs directory
        if all(word not in path for word in EXCLUDED_STR):
            dirs.append(path)

    for d in os.listdir(path):
        new_path = os.path.join(path, d)
        if os.path.isdir(new_path):
            dirs += get_tf_dirs(path=new_path, file_ext=file_ext)

    return dirs
