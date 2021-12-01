import os
from fnmatch import fnmatch

for dirpath, dirnames, filenames in os.walk(os.curdir):
    for file in filenames:
        if fnmatch(file, '*.gitignore'):
            print("Found .gitignore in {}. Deleting.".format(os.path.join(dirpath, file)))
            os.remove(os.path.join(dirpath, file))