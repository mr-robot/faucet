import os
import imp
import importlib
import sys


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


def my_import(name):
    """
    Helper function to import a module based on a module name

    :param name:
    :return:
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class ConfigStruct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def get_union():
    union = imp.load_source("union", os.path.join(os.getcwd(), "union.py"))

    return union.routes


def load_class(full_class_string):
    """
    Helper function to dynamically load a class from a string
    from http://thomassileo.com/blog/2012/12/21/dynamically-load-python-modules-or-classes/
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)


def get_working_path(working_path, message_id):
    return os.path.join(working_path, ("%s_%s" % (message_id, ".tmp")))


def import_from_sibing(path):
    sys.path.append(os.path.abspath(path))