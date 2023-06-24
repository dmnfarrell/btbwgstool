# -*- coding: utf-8 -*-

"""
    Qt widgets for snpgenie.
    Created Jan 2020
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys, os, io, platform
import numpy as np
import pandas as pd
import pylab as plt
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import string
from .qt import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
#from . import plotting

module_path = os.path.dirname(os.path.abspath(__file__))
iconpath = os.path.join(module_path, 'icons')

def createButton(parent, name, function, iconname=None, iconsize=20):
    """Create a button for a function and optional icon.
        Returns:
            the button widget
    """

    button = QPushButton(parent)
    button.setGeometry(QtCore.QRect(30,40,30,40))
    button.setText(name)
    iconfile = os.path.join(iconpath,iconname)
    icon = QIcon(iconfile)
    button.setIcon(QIcon(icon))
    button.setIconSize(QtCore.QSize(iconsize,iconsize))
    button.clicked.connect(function)
    button.setMinimumWidth(30)
    return button

def dialogFromOptions(parent, opts, sections=None,
                      sticky='news', wrap=2, section_wrap=2, style=None):
    """Get Qt widgets dialog from a dictionary of options"""

    sizepolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    sizepolicy.setHorizontalStretch(1)
    sizepolicy.setVerticalStretch(0)

    if style == None:
        style = '''
        QWidget {
            font-size: 12px;
        }
        QWidget {
            max-width: 130px;
            min-width: 30px;
            font-size: 14px;
        }
        QPlainTextEdit {
            max-height: 80px;
        }
        QComboBox {
            combobox-popup: 0;
            max-height: 30px;
            max-width: 100px;
        }
        '''

    if sections == None:
        sections = {'options': opts.keys()}

    widgets = {}
    dialog = QWidget(parent)
    dialog.setSizePolicy(sizepolicy)

    l = QGridLayout(dialog)
    l.setSpacing(2)
    l.setAlignment(QtCore.Qt.AlignLeft)
    scol=1
    srow=1
    for s in sections:
        row=1
        col=1
        f = QGroupBox()
        f.setSizePolicy(sizepolicy)
        f.setTitle(s)
        #f.resize(50,100)
        #f.sizeHint()
        l.addWidget(f,srow,scol)
        gl = QGridLayout(f)
        gl.setAlignment(QtCore.Qt.AlignTop)
        srow+=1
        #gl.setSpacing(10)
        for o in sections[s]:
            label = o
            val = None
            opt = opts[o]
            if 'label' in opt:
                label = opt['label']
            val = opt['default']
            t = opt['type']
            lbl = QLabel(label)
            gl.addWidget(lbl,row,col)
            lbl.setStyleSheet(style)
            if t == 'combobox':
                w = QComboBox()
                w.addItems(opt['items'])
                if 'editable' in opt:
                     w.setEditable(True)
                try:
                    w.setCurrentIndex(opt['items'].index(str(opt['default'])))
                except:
                    w.setCurrentIndex(0)
            elif t == 'entry':
                w = QLineEdit()
                w.setText(str(val))
            elif t == 'textarea':
                w = QPlainTextEdit()
                w.insertPlainText(str(val))
            elif t == 'slider':
                w = QSlider(QtCore.Qt.Horizontal)
                s,e = opt['range']
                w.setTickInterval(opt['interval'])
                w.setSingleStep(opt['interval'])
                w.setMinimum(s)
                w.setMaximum(e)
                w.setTickPosition(QSlider.TicksBelow)
                w.setValue(val)
            elif t == 'spinbox':
                if type(val) is float:
                    w = QDoubleSpinBox()
                else:
                    w = QSpinBox()
                w.setValue(val)
                if 'range' in opt:
                    min,max=opt['range']
                    w.setRange(min,max)
                    w.setMinimum(min)
                if 'interval' in opt:
                    w.setSingleStep(opt['interval'])
            elif t == 'checkbox':
                w = QCheckBox()
                w.setChecked(val)
            elif t == 'font':
                w = QFontComboBox()
                w.resize(w.sizeHint())
                w.setCurrentIndex(1)
            if 'width' in opt:
                h=20
                if 'height' in opt:
                    h=opt['height']
                w.setMinimumSize(opt['width'],h)
                w.resize(QtCore.QSize(opt['width'], h))

            #policy = dialog.sizePolicy()
            #policy.setVerticalStretch(1)
            #w.setSizePolicy(policy)

            col+=1
            gl.addWidget(w,row,col)
            w.setStyleSheet(style)
            widgets[o] = w
            #print (o, row, col)
            if col>=wrap:
                col=1
                row+=1
            else:
                col+=2
        if scol >= section_wrap:
            scol=1
        else:
            scol+=1
    return dialog, widgets

def getWidgetValues(widgets):
    """Get values back from a set of widgets"""

    kwds = {}
    for i in widgets:
        val = None
        if i in widgets:
            w = widgets[i]
            if type(w) is QLineEdit:
                try:
                    val = float(w.text())
                except:
                    val = w.text()
            elif type(w) is QPlainTextEdit:
                val = w.toPlainText()
            elif type(w) is QComboBox or type(w) is QFontComboBox:
                val = w.currentText()
            elif type(w) is QCheckBox:
                val = w.isChecked()
            elif type(w) is QSlider:
                val = w.value()
            elif type(w) in [QSpinBox,QDoubleSpinBox]:
                val = w.value()
            if val != None:
                kwds[i] = val
    kwds = kwds
    return kwds

def setWidgetValues(widgets, values):
    """Set values for a set of widgets from a dict"""

    kwds = {}
    for i in values:
        val = values[i]
        if i in widgets:
            #print (i, val, type(val))
            w = widgets[i]
            if type(w) is QLineEdit:
                w.setText(str(val))
            elif type(w) is QPlainTextEdit:
                w.insertPlainText(str(val))
            elif type(w) is QComboBox or type(w) is QFontComboBox:
                index = w.findText(val)
                w.setCurrentIndex(index)
            elif type(w) is QCheckBox:
                w.setChecked(val)
            elif type(w) is QSlider:
                w.setValue(val)
            elif type(w) in [QSpinBox,QDoubleSpinBox]:
                w.setValue(val)
    return

def addToolBarItems(toolbar, parent, items):
    """Populate toolbar from dict of items"""

    for i in items:
        if 'file' in items[i]:
            iconfile = os.path.join(iconpath,items[i]['file'])
            icon = QIcon(iconfile)
        else:
            icon = QIcon.fromTheme(items[i]['icon'])
        btn = QAction(icon, i, parent)
        btn.triggered.connect(items[i]['action'])
        if 'shortcut' in items[i]:
            btn.setShortcut(QKeySequence(items[i]['shortcut']))
        #btn.setCheckable(True)
        toolbar.addAction(btn)
    return toolbar

def get_fonts():
     """Get the current list of system fonts"""

     import matplotlib.font_manager
     l = matplotlib.font_manager.findSystemFonts(fontext='ttf')
     fonts = []
     for fname in l:
        try: fonts.append(matplotlib.font_manager.FontProperties(fname=fname).get_name())
        except RuntimeError: pass
     fonts = list(set(fonts))
     fonts.sort()
     return fonts

class MultipleInputDialog(QDialog):
    """Qdialog with multiple inputs"""
    def __init__(self, parent, options=None, title='Input', width=400, height=200):
        super(MultipleInputDialog, self).__init__(parent)
        self.values = None
        self.accepted = False
        self.setMinimumSize(width, height)
        self.setWindowTitle(title)
        dialog, self.widgets = dialogFromOptions(self, options)
        vbox = QVBoxLayout(self)
        vbox.addWidget(dialog)
        buttonbox = QDialogButtonBox(self)
        buttonbox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        buttonbox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        buttonbox.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        vbox.addWidget(buttonbox)
        self.show()
        return self.values

    def accept(self):
        self.values = getWidgetValues(self.widgets)
        self.accepted = True
        self.close()
        return

class ToolBar(QWidget):
    """Toolbar class"""
    def __init__(self, table, parent=None):
        super(ToolBar, self).__init__(parent)
        self.parent = parent
        self.table = table
        self.layout = QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.layout)
        self.createButtons()
        self.setMaximumWidth(40)
        return

    def createButtons(self):

        funcs = {'load':self.table.load, 'save':self.table.save,
                 'importexcel': self.table.load,
                 'copy':self.table.copy, 'paste':self.table.paste,
                 'plot':self.table.plot,
                 'transpose':self.table.pivot,
                 'pivot':self.table.pivot}
        icons = {'load': 'document-new', 'save': 'document-save-as',
                 'importexcel': 'x-office-spreadsheet',
                 'copy': 'edit-copy', 'paste': 'edit-paste',
                 'plot':'insert-image',
                 'transpose':'object-rotate-right',
                 'pivot': 'edit-undo',
                 }
        for name in funcs:
            self.addButton(name, funcs[name], icons[name])

    def addButton(self, name, function, icon):

        layout=self.layout
        button = QPushButton(name)
        button.setGeometry(QtCore.QRect(30,40,30,40))
        button.setText('')
        iconw = QIcon.fromTheme(icon)
        button.setIcon(QIcon(iconw))
        button.setIconSize(QtCore.QSize(20,20))
        button.clicked.connect(function)
        button.setMinimumWidth(30)
        layout.addWidget(button)

class BasicDialog(QDialog):
    """Qdialog for table operations interfaces"""
    def __init__(self, parent, table, title=None):

        super(BasicDialog, self).__init__(parent)
        self.parent = parent
        self.table = table
        self.df = table.model.df
        #self.app = self.parent.app
        self.setWindowTitle(title)
        self.createWidgets()
        self.setGeometry(QtCore.QRect(400, 300, 1000, 600))
        self.show()
        return

    def createWidgets(self):
        """Create widgets - override this"""

        cols = list(self.df.columns)

    def createButtons(self, parent):

        bw = self.button_widget = QWidget(parent)
        vbox = QVBoxLayout(bw)
        vbox.setAlignment(QtCore.Qt.AlignTop)
        button = QPushButton("Apply")
        button.clicked.connect(self.apply)
        vbox.addWidget(button)
        button = QPushButton("Update")
        button.clicked.connect(self.update)
        vbox.addWidget(button)
        button = QPushButton("Copy to clipboard")
        button.clicked.connect(self.copy_to_clipboard)
        vbox.addWidget(button)
        button = QPushButton("Close")
        button.clicked.connect(self.close)
        vbox.addWidget(button)
        return bw

    def apply(self):
        """Override this"""
        return

    def update(self):
        """Update the original table"""

        self.table.model.df = self.result.model.df
        self.table.refresh()
        self.close()
        return

    def copy_to_clipboard(self):
        """Copy result to clipboard"""

        df = self.result.model.df
        df.to_clipboard()
        return

    def close(self):
        self.destroy()
        return

class MergeDialog(BasicDialog):
    """Dialog to melt table"""
    def __init__(self, parent, table, df2, title='Merge Tables'):
        self.table = table
        self.df = table.model.df
        self.df2 = df2
        BasicDialog.__init__(self, parent, table, title)
        return

    def createWidgets(self):
        """Create widgets"""

        cols = self.df.columns
        cols2 = self.df2.columns
        ops = ['merge','concat']
        how = ['inner','outer','left','right']
        hbox = QHBoxLayout(self)
        main = QWidget(self)
        main.setMaximumWidth(300)
        hbox.addWidget(main)

        l = QVBoxLayout(main)
        w = self.ops_w = QComboBox(main)
        w.addItems(ops)
        l.addWidget(QLabel('Operation'))
        l.addWidget(w)
        w = self.lefton_w = QListWidget(main)
        w.setSelectionMode(QAbstractItemView.MultiSelection)
        w.addItems(cols)
        l.addWidget(QLabel('Left on'))
        l.addWidget(w)
        w = self.righton_w = QListWidget(main)
        w.setSelectionMode(QAbstractItemView.MultiSelection)
        w.addItems(cols2)
        l.addWidget(QLabel('Right on'))
        l.addWidget(w)

        w = self.leftindex_w = QCheckBox(main)
        w.setChecked(False)
        l.addWidget(QLabel('Use left index'))
        l.addWidget(w)
        w = self.rightindex_w = QCheckBox(main)
        w.setChecked(False)
        l.addWidget(QLabel('Use right index'))
        l.addWidget(w)

        w = self.how_w = QComboBox(main)
        w.addItems(how)
        l.addWidget(QLabel('How'))
        l.addWidget(w)

        w = self.left_suffw = QLineEdit('_1')
        l.addWidget(QLabel('Left suffix'))
        l.addWidget(w)
        w = self.right_suffw = QLineEdit('_2')
        l.addWidget(QLabel('Right suffix'))
        l.addWidget(w)

        from . import tables
        self.result = tables.DataFrameTable(self)
        hbox.addWidget(self.result)
        bf = self.createButtons(self)
        hbox.addWidget(bf)
        return

    def updateColumns(self):

        #self.df2 =
        cols2 = self.df2.columns
        return

    def apply(self):
        """Do the operation"""

        left_index = self.leftindex_w.isChecked()
        right_index = self.rightindex_w.isChecked()
        if left_index == True:
            lefton = None
        else:
            lefton = [i.text() for i in self.lefton_w.selectedItems()]
        if right_index == True:
            righton = None
        else:
            righton = [i.text() for i in self.righton_w.selectedItems()]
        how = self.how_w.currentText()
        op = self.ops_w.currentText()
        if op == 'merge':
            res = pd.merge(self.df, self.df2,
                            left_on=lefton,
                            right_on=righton,
                            left_index=left_index,
                            right_index=right_index,
                            how=how,
                            suffixes=(self.left_suffw .text(),self.right_suffw.text())
                            )
        else:
            res = pd.concat([self.df, self.df2])
        self.result.model.df = res
        self.result.refresh()
        return

class BaseOptions(object):
    """Class to generate widget dialog for dict of options"""
    def __init__(self, parent=None, opts={}, groups={}):
        """Setup variables"""

        self.parent = parent
        self.groups = groups
        self.opts = opts
        return

    def applyOptions(self):
        """Set the plot kwd arguments from the widgets"""

        self.kwds = getWidgetValues(self.widgets)
        return

    def apply(self):
        self.applyOptions()
        if self.callback != None:
            self.callback()
        return

    def showDialog(self, parent, wrap=2, section_wrap=2, style=None):
        """Auto create tk vars, widgets for corresponding options and
           and return the frame"""

        dialog, self.widgets = dialogFromOptions(parent, self.opts, self.groups,
                                wrap=wrap, section_wrap=section_wrap, style=style)
        return dialog

    def setWidgetValue(self, key, value):
        "Set a widget value"

        setWidgetValues(self.widgets, {key: value})
        self.applyOptions()
        return

    def updateWidgets(self, kwds):

        for k in kwds:
            setWidgetValues(self.widgets, {k: kwds[k]})
        return

    def increment(self, key, inc):
        """Increase the value of a widget"""

        new = self.kwds[key]+inc
        self.setWidgetValue(key, new)
        return

class DynamicDialog(QDialog):
    """Dynamic form using baseoptions"""

    def __init__(self, parent=None, options={}, groups=None, title='Dialog'):
        super(DynamicDialog, self).__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.opts = BaseOptions(self, options, groups)
        dialog = self.opts.showDialog(self, wrap=1, section_wrap=1)
        layout.addWidget(dialog)
        buttonbox = QDialogButtonBox(self)
        buttonbox.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttonbox.addButton("Ok", QDialogButtonBox.AcceptRole)
        self.connect(buttonbox, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttonbox, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        layout.addWidget(buttonbox)
        return

    def get_values():
        """Get the widget values"""

        kwds = self.opts.kwds
        return kwds

class Editor(QTextEdit):
    def __init__(self, parent=None, fontsize=12, **kwargs):
        super(Editor, self).__init__(parent, **kwargs)
        font = QFont("Monospace")
        font.setPointSize(fontsize)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        return

    def zoom(self, delta):
        if delta < 0:
            self.zoomOut(1)
        elif delta > 0:
            self.zoomIn(1)

    def contextMenuEvent(self, event):

        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        clearAction = menu.addAction("Clear")
        zoominAction = menu.addAction("Zoom In")
        zoomoutAction = menu.addAction("Zoom Out")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            self.copy()
        elif action == clearAction:
            self.clear()
        elif action == zoominAction:
            self.zoom(1)
        elif action == zoomoutAction:
            self.zoom(-1)

    def insert(self, txt):

        self.insertPlainText(txt)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        return

class PlainTextEditor(QPlainTextEdit):
    def __init__(self, parent=None, **kwargs):
        super(PlainTextEditor, self).__init__(parent, **kwargs)
        font = QFont("Monospace")
        font.setPointSize(10)
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)
        return

    def zoom(self, delta):
        if delta < 0:
            self.zoomOut(1)
        elif delta > 0:
            self.zoomIn(1)

    def contextMenuEvent(self, event):

        menu = QMenu(self)
        copyAction = menu.addAction("Copy")
        clearAction = menu.addAction("Clear")
        zoominAction = menu.addAction("Zoom In")
        zoomoutAction = menu.addAction("Zoom Out")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == copyAction:
            self.copy()
        elif action == clearAction:
            self.clear()
        elif action == zoominAction:
            self.zoom(1)
        elif action == zoomoutAction:
            self.zoom(-1)

class TextViewer(QDialog):
    """Sequence records features viewer using dna_features_viewer"""
    def __init__(self, parent=None, text='', title='Text'):

        super(TextViewer, self).__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(QtCore.QRect(200, 200, 1000, 400))
        self.setMinimumHeight(150)
        self.add_widgets()
        self.ed.appendPlainText(text)
        return

    def add_widgets(self):
        """Add widgets"""

        l = QVBoxLayout(self)
        self.setLayout(l)
        font = QFont("Monospace")
        font.setPointSize(10)
        font.setStyleHint(QFont.TypeWriter)
        self.ed = ed = PlainTextEditor(self, readOnly=True)
        self.ed.setFont(font)
        l.addWidget(self.ed)
        self.show()

class FileViewer(QDialog):
    """Sequence records features viewer"""
    def __init__(self, parent=None, filename=None):

        #QDialog.__init__(self)
        super(FileViewer, self).__init__(parent)
        self.ed = ed = QPlainTextEdit(self, readOnly=True)
        #ed.setStyleSheet("font-family: monospace; font-size: 14px;")
        font = QFont("Monospace")
        font.setPointSize(10)
        font.setStyleHint(QFont.TypeWriter)
        self.ed.setFont(font)
        self.setWindowTitle('sequence features')
        self.setGeometry(QtCore.QRect(200, 200, 800, 800))
        #self.setCentralWidget(ed)
        l = QVBoxLayout(self)
        self.setLayout(l)
        l.addWidget(ed)
        self.show()

    def show_records(self, recs, format='genbank'):

        from Bio import SeqIO
        recs = SeqIO.to_dict(recs)
        if format == 'genbank':
            for r in recs:
                self.ed.appendPlainText(recs[r].format('genbank'))
        elif format == 'gff':
            tools.save_gff(recs,'temp.gff')
            f = open('temp.gff','r')
            for l in f.readlines():
                self.ed.appendPlainText(l)
        recnames = list(recs.keys())
        return

class TableViewer(QDialog):
    """View row of data in table"""
    def __init__(self, parent=None, dataframe=None, **kwargs):
        super(TableViewer, self).__init__(parent)
        self.setGeometry(QtCore.QRect(200, 200, 600, 600))
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.table = tables.DataFrameTable(self, dataframe, **kwargs)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.addWidget(self.table)
        return

    def setDataFrame(self, dataframe):
        self.table.model.df = dataframe
        return

class PlotWidget(FigureCanvas):
    """Basic mpl plot view"""

    def __init__(self, parent=None, figure=None, dpi=100, hold=False):

        if figure == None:
            figure = Figure()
        super(PlotWidget, self).__init__(figure)
        self.setParent(parent)
        self.figure = Figure(dpi=dpi)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

class PlotOptions(BaseOptions):
    """Class to provide a dialog for plot options"""

    def __init__(self, parent=None):
        """Setup variables"""

        self.parent = parent
        self.kwds = {}
        kinds = ['','bar','barh','hist','scatter','line','heatmap','pie','box']
        scales = ['linear','log']
        style_list = ['default', 'classic', 'fivethirtyeight',
                     'seaborn-pastel','seaborn-whitegrid', 'ggplot','bmh',
                     'grayscale','dark_background']
        markers = ['','o','.','^','v','>','<','s','+','x','p','d','h','*']
        linestyles = ['-','--','-.',':']
        fonts = get_fonts()
        if 'Windows' in platform.platform():
            defaultfont = 'Arial'
        else:
            defaultfont = 'FreeSans'
        colormaps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
        self.groups = {'general':['kind','grid','bins','linewidth','linestyle',
                       'marker','ms','alpha','colormap'],
                       'format' :['title','xlabel','style','font','fontsize']
                       }
        self.opts = {
                    'kind':{'type':'combobox','default':'','items':kinds},
                    'grid':{'type':'checkbox','default':0,'label':'show grid'},
                    'bins':{'type':'spinbox','default':20,'width':5},
                    'marker':{'type':'combobox','default':'o','items': markers},
                    'linestyle':{'type':'combobox','default':'-','items': linestyles},
                    'linewidth':{'type':'doublespinbox','default':1.0,'range':(0,20),'interval':.2,'label':'line width'},
                    'ms':{'type':'spinbox','default':30,'range':(1,120),'interval':1,'label':'marker size'},
                    'colormap':{'type':'combobox','default':'Spectral','items':colormaps},
                    'alpha':{'type':'doublespinbox','default':0.9,'range':(.1,1),'interval':.1,'label':'alpha'},
                    'style':{'type':'combobox','default':'bmh','items': style_list},
                    'title':{'type':'entry','default':''},
                    'xlabel':{'type':'entry','default':''},
                    'font':{'type':'font','default':defaultfont,'items':fonts},
                    'fontsize':{'type':'spinbox','default':10,'range':(4,50),'label':'font size'},
                    }
        return

class PlotViewer(QWidget):
    """matplotlib plots widget"""
    def __init__(self, parent=None, controls=True):

        super(PlotViewer, self).__init__(parent)
        self.setGeometry(QtCore.QRect(200, 200, 900, 600))
        self.main = QSplitter()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.main)
        self.create_figure()
        if controls == True:
            self.create_controls()
        self.setWindowTitle('plots')
        return

    def create_figure(self, fig=None):
        """Create canvas and figure"""

        from matplotlib.backends.backend_qt5agg import FigureCanvas
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        import matplotlib.pyplot as plt
        #ax.plot(range(10))
        if fig == None:
            fig, ax = plt.subplots(1,1, figsize=(7,5), dpi=120)
            self.ax = ax
        if hasattr(self, 'canvas'):
            self.layout().removeWidget(self.canvas)
        canvas = FigureCanvas(fig)
        left = QWidget()
        self.main.addWidget(left)
        l = QVBoxLayout()
        left.setLayout(l)
        l.addWidget(canvas)
        self.toolbar = NavigationToolbar(canvas, self)
        l.addWidget(self.toolbar)
        self.fig = fig
        self.canvas = canvas
        iconfile = os.path.join(iconpath,'reduce')
        a = QAction(QIcon(iconfile), "Reduce elements",  self)
        a.triggered.connect(lambda: self.zoom(zoomin=False))
        self.toolbar.addAction(a)
        iconfile = os.path.join(iconpath,'enlarge')
        a = QAction(QIcon(iconfile), "Enlarge elements",  self)
        a.triggered.connect(lambda: self.zoom(zoomin=True))
        self.toolbar.addAction(a)
        return

    def create_controls(self):
        """Make widgets for options"""

        self.opts = PlotOptions()
        right = QWidget()
        self.main.addWidget(right)
        w = self.opts.showDialog(self, style=None, section_wrap=1)
        right.setMaximumWidth(220)
        l = QVBoxLayout()
        right.setLayout(l)
        l.addWidget(w)
        btn = QPushButton('Refresh')
        btn.clicked.connect(self.replot)
        l.addWidget(btn)
        self.main.addWidget(right)
        return

    def plot(self, data, kind=None):
        """Do plot"""

        self.opts.applyOptions()
        kwds = self.opts.kwds
        if kind == None and kwds['kind'] != '':
            #overrides kind argument
            kind = kwds['kind']
        else:
            #set widget to current plot kind
            self.opts.setWidgetValue('kind', kind)
            pass
        title = kwds['title']
        xlabel = kwds['xlabel']
        font = kwds['font']
        fontsize = kwds['fontsize']
        alpha = kwds['alpha']
        cmap = kwds['colormap']
        grid = kwds['grid']
        marker = kwds['marker']
        ms = kwds['ms']
        ls = kwds['linestyle']
        lw = kwds['linewidth']
        self.style = kwds['style']
        self.set_style()
        self.data = data
        #self.kind = kind

        d = data._get_numeric_data()
        xcol = d.columns[0]
        ycols = d.columns[1:]

        nrows = int(round(np.sqrt(len(data.columns)),0))
        layout = (nrows,-1)
        self.clear()
        fig = self.fig
        ax = self.ax
        plt.rc("font", family=kwds['font'], size=fontsize)
        if kind == 'bar':
            d.plot(kind='bar',ax=ax, cmap=cmap, grid=grid, alpha=alpha, linewidth=lw,
                    fontsize=fontsize)
        elif kind == 'barh':
            d.plot(kind='barh',ax=ax, cmap=cmap, grid=grid, alpha=alpha, linewidth=lw,
                    fontsize=fontsize)
        elif kind == 'hist':
            d.plot(kind='hist',subplots=True,ax=ax,bins=kwds['bins'], linewidth=lw,
                    cmap=cmap, grid=grid, alpha=alpha, fontsize=fontsize)
        elif kind == 'scatter':
            d=d.dropna()
            d.plot(x=xcol,y=ycols,kind='scatter',ax=ax,s=ms,marker=marker,
                    grid=grid, alpha=alpha, fontsize=fontsize)
        elif kind == 'line':
            d.plot(kind='line',ax=ax, cmap=cmap, grid=grid, alpha=alpha, linewidth=lw,
                    fontsize=fontsize)
        elif kind == 'heatmap':
            #ax.imshow(d, cmap=cmap)
            self.heatmap(d, ax, cmap=cmap, alpha=alpha)
        elif kind == 'pie':
            d.plot(kind='pie',subplots=True,legend=False,layout=layout,ax=ax)
        elif kind == 'box':
            d.boxplot(ax=ax, grid=grid)

        if xlabel != '':
            ax.set_xlabel(xlabel)
        fig.suptitle(title, font=font)
        plt.tight_layout()
        self.redraw()
        return

    def replot(self):
        """Update current plot"""

        self.plot(self.data, kind=None)
        return

    def refresh(self):
        """Update current plot"""

        self.plot(self.data, kind=None)
        return

    def heatmap(self, df, ax, cmap='Blues', alpha=0.9, lw=1,
                colorbar=True, cscale='log'):
        """Plot heatmap"""

        X = df._get_numeric_data()
        clr='black'
        if lw==0:
            clr=None
            lw=None
        if cscale == 'log':
            norm=mpl.colors.LogNorm()
        else:
            norm=None
        hm = ax.pcolor(X, cmap=cmap,linewidth=lw,alpha=alpha,norm=norm)
        if colorbar == True:
            self.fig.colorbar(hm, ax=ax)
        ax.set_xticks(np.arange(0.5, len(X.columns)))
        ax.set_yticks(np.arange(0.5, len(X.index)))
        ax.set_xticklabels(X.columns, minor=False)
        ax.set_yticklabels(X.index, minor=False)
        ax.set_ylim(0, len(X.index))
        return

    def violinplot(self, df, ax, kwds):
        """violin plot"""

        data=[]
        clrs=[]
        df = df._get_numeric_data()
        cols = len(df.columns)
        cmap = plt.cm.get_cmap(kwds['colormap'])
        for i,d in enumerate(df):
            clrs.append(cmap(float(i)/cols))
            data.append(df[d].values)
        lw = kwds['linewidth']
        alpha = kwds['alpha']
        parts = ax.violinplot(data, showextrema=False, showmeans=True)
        i=0
        for pc in parts['bodies']:
            pc.set_facecolor(clrs[i])
            pc.set_edgecolor('black')
            pc.set_alpha(alpha)
            pc.set_linewidth(lw)
            i+=1
        labels = df.columns
        ax.set_xticks(np.arange(1, len(labels) + 1))
        ax.set_xticklabels(labels)
        return

    def set_figure(self, fig):
        """Set the figure if we have plotted elsewhere"""

        self.clear()
        self.create_figure(fig)
        #self.ax = fig.ax
        self.canvas.draw()
        return

    def clear(self):
        """Clear plot"""

        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.canvas.draw()
        return

    def set_style(self):
        """Apply style"""

        if self.style == None or self.style == '':
            mpl.rcParams.update(mpl.rcParamsDefault)
        else:
            plt.style.use(self.style)
        return

    def redraw(self):
        self.canvas.draw()

    def zoom(self, zoomin=True):
        """Zoom in/out to plot by changing size of elements"""

        if zoomin == False:
            val=-1.0
        else:
            val=1.0
        if len(self.opts.kwds) == 0:
            return
        self.opts.increment('linewidth',val/5)
        self.opts.increment('ms',val*2)
        self.opts.increment('fontsize',val)
        self.replot()
        return

class CustomPlotViewer(PlotViewer):
    """Custom plot view with interactions"""
    def __init__(self, parent=None, controls=True, app=None):
        super(CustomPlotViewer, self).__init__(parent, controls)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        #self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.app = app
        return

    def onpress(self, event):

        return

    def onclick(self, event):

        x,y = event.xdata, event.ydata
        print('click: %s,%s' %(x,y))
        #c = plt.Circle([x,y], 600, color='g', alpha=.5)
        #self.ax.add_patch(c)
        self.canvas.draw()
        df = self.app.cent
        pad=500
        found = df.cx[x-pad:x+pad, y-pad:y+pad]
        if len(found)>0:
            self.app.sample_details(found.iloc[0])
        return

    def onpick(event):
        """Pick event"""

        ind = event.ind
        print (ind)
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))


class BrowserViewer(QDialog):
    """matplotlib plots widget"""
    def __init__(self, parent=None):

        super(BrowserViewer, self).__init__(parent)
        self.add_widgets()
        return

    def add_widgets(self):
        """Add widgets"""

        layout = self.layout = QVBoxLayout()
        self.main = QWidget()
        vbox = QVBoxLayout(self.main)
        layout.addWidget(self.main)
        from PySide2.QtWebEngineWidgets import QWebEngineView
        self.browser = QWebEngineView()
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(self.browser)
        self.browser.setMinimumHeight(500)

        toolswidget = QWidget()
        toolswidget.setMaximumHeight(100)

        vbox.addWidget(toolswidget)
        l = QVBoxLayout(toolswidget)
        self.zoomslider = w = QSlider(QtCore.Qt.Horizontal)
        w.setSingleStep(5)
        w.setMinimum(5)
        w.setMaximum(50)
        w.setValue(10)
        l.addWidget(w)
        w.valueChanged.connect(self.zoom)
        return

    def load_page(self, url):
        self.browser.setUrl(url)

    def zoom(self):
        zoom = self.zoomslider.value()/10
        self.browser.setZoomFactor(zoom)

class FoliumViewer(QWidget):
    """folium plot widget"""
    def __init__(self, parent=None):
        super(FoliumViewer, self).__init__(parent)
        self.main = QWebEngineView()
        l = QVBoxLayout()
        self.setLayout(l)
        l.addWidget(self.main)
        #l.addWidget(QLabel('test'))
        #self.test()
        return

    def test(self):
        code = '<html> HELLO </html>'
        self.main.setHtml(code)
        return

    def refresh(self, location=[54.1, -7.0]):
        """Update map"""

        import folium
        #print (location)
        m = folium.Map(location=location, tiles='Stamen Terrain', #crs='EPSG29902',
                         width=300, height=300)
        style1 = {'fillColor': 'blue', 'color': 'black','weight':2}
        data = io.BytesIO()
        m.save(data, close_file=False)
        #print (data.getvalue().decode())
        self.main.setHtml(data.getvalue().decode())
        return

class ScratchPad(QWidget):
    """Temporary storage widget for plots and other items.
    Currently supports storing text, mpl figures and dataframes"""
    def __init__(self, parent=None):
        super(ScratchPad, self).__init__(parent)
        self.parent = parent
        self.setMinimumSize(400,300)
        self.setGeometry(QtCore.QRect(300, 200, 800, 600))
        self.setWindowTitle("Scratchpad")
        self.createWidgets()
        sizepolicy = QSizePolicy()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        #dict to store objects, these should be serialisable
        self.items = {}
        return

    def createWidgets(self):
        """Create widgets. Plot on left and dock for tools on right."""

        self.main = QTabWidget(self)
        self.main.setTabsClosable(True)
        self.main.tabCloseRequested.connect(lambda index: self.remove(index))
        layout = QVBoxLayout(self)
        toolbar = QToolBar("toolbar")
        layout.addWidget(toolbar)
        items = { 'new text':{'action':self.newText,'file':'document-new'},
                  'save': {'action':self.save,'file':'save'},
                  'save all': {'action':self.saveAll,'file':'save-all'},
                  'clear': {'action':self.clear,'file':'clear'}
                    }
        for i in items:
            if 'file' in items[i]:
                iconfile = os.path.join(iconpath,items[i]['file']+'.png')
                icon = QIcon(iconfile)
            else:
                icon = QIcon.fromTheme(items[i]['icon'])
            btn = QAction(icon, i, self)
            btn.triggered.connect(items[i]['action'])
            toolbar.addAction(btn)
        layout.addWidget(self.main)
        return

    def update(self, items):
        """Display a dict of stored objects"""

        self.main.clear()
        for name in items:
            obj = items[name]
            #print (name,type(obj))
            if type(obj) is str:
                te = dialogs.PlainTextEditor()
                te.setPlainText(obj)
                self.main.addTab(te, name)
            elif type(obj) is pd.DataFrame:
                tw = core.DataFrameTable(self.main, dataframe=obj)
                self.main.addTab(tw, name)
            else:
                pw = PlotWidget(self.main)
                self.main.addTab(pw, name)
                pw.figure = obj
                pw.draw()
                plt.tight_layout()
        self.items = items
        return

    def remove(self, idx):
        """Remove selected tab and item widget"""

        index = self.main.currentIndex()
        name = self.main.tabText(index)
        del self.items[name]
        self.main.removeTab(index)
        return

    def save(self):
        """Save selected item"""

        index = self.main.currentIndex()
        name = self.main.tabText(index)
        suff = "PNG files (*.png);;JPG files (*.jpg);;PDF files (*.pdf);;All files (*.*)"
        filename, _ = QFileDialog.getSaveFileName(self, "Save Figure", name, suff)
        if not filename:
            return

        fig = self.items[name]
        fig.savefig(filename+'.png', dpi=core.DPI)
        return

    def saveAll(self):
        """Save all figures in a folder"""

        dir =  QFileDialog.getExistingDirectory(self, "Save Folder",
                                             homepath, QFileDialog.ShowDirsOnly)
        if not dir:
            return
        for name in self.items:
            fig = self.items[name]
            fig.savefig(os.path.join(dir,name+'.png'), dpi=core.DPI)
        return

    def clear(self):
        """Clear plots"""

        self.items.clear()
        self.main.clear()
        return

    def newText(self):
        """Add a text editor"""

        name, ok = QInputDialog.getText(self, 'Name', 'Name:',
                    QLineEdit.Normal, '')
        if ok:
            tw = dialogs.PlainTextEditor()
            self.main.addTab(tw, name)
            self.items[name] = tw.toPlainText()
        return

    def closeEvent(self, event):
        """Close"""

        for idx in range(self.main.count()):
            name = self.main.tabText(idx)
            #print (name)
            w = self.main.widget(idx)
            #print (w)
            if type(w) == dialogs.PlainTextEditor:
                self.items[name] = w.toPlainText()
        return