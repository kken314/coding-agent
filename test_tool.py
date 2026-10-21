import os

def list_files(path="."):
    names = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            name += "/"
        names.append(name)
    return "\n".join(names)

print(list_files("src/coding_agent/"))