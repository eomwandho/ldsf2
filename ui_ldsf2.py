# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_ldsf2.ui'
#
# Created: Fri Jun 27 20:36:38 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ldsf2(object):
    def setupUi(self, ldsf2):
        ldsf2.setObjectName(_fromUtf8("ldsf2"))
        ldsf2.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(ldsf2)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(ldsf2)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ldsf2.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ldsf2.reject)
        QtCore.QMetaObject.connectSlotsByName(ldsf2)

    def retranslateUi(self, ldsf2):
        ldsf2.setWindowTitle(QtGui.QApplication.translate("ldsf2", "ldsf2", None, QtGui.QApplication.UnicodeUTF8))

