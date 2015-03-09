
PyObject = 'QVariant'

# define global variables
def py2q(py_object):
    return py_object

def q2py(q_variant, default=None):
    return q_variant

# backwards compat
def wrapNone(value):
    if value is None:
        return QtCore.THREADSAFE_NONE
    else:
        return value

def unwrapNone(value):
    if value is QtCore.THREADSAFE_NONE:
        return None
    else:
        return value