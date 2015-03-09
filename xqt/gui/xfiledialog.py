
from xqt import QtGui

class XFileDialog(QtGui.QFileDialog):
    @staticmethod
    def getOpenFileName(*args):
        """
        Normalizes the getOpenFileName method between the different Qt
        wrappers.
        
        :return     (<str> filename, <bool> accepted)
        """
        result = QtGui.QFileDialog.getOpenFileName(*args)
        
        # PyQt4 returns just a string
        if type(result) is not tuple:
            return result, bool(result)
        
        # PySide returns a tuple of str, bool
        else:
            return result

    @staticmethod
    def getDirectory(*args):
        """
        Normalizes the getDirectory method between the different Qt
        wrappers.
        
        :return     (<str> filename, <bool> accepted)
        """
        result = QtGui.QFileDialog.getDirectory(*args)
        
        # PyQt4 returns just a string
        if type(result) is not tuple:
            return result, bool(result)
        
        # PySide returns a tuple of str, bool
        else:
            return result

    @staticmethod
    def getSaveFileName(*args):
        """
        Normalizes the getSaveFileName method between the different Qt
        wrappers.
        
        :return     (<str> filename, <bool> accepted)
        """
        result = QtGui.QFileDialog.getSaveFileName(*args)
        
        # PyQt4 returns just a string
        if type(result) is not tuple:
            return result, bool(result)
        
        # PySide returns a tuple of str, bool
        else:
            return result

