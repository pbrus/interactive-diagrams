#!/usr/bin/env python3

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter as tefo
from idgrms.data import *
from idgrms.plotdgrms import *


argparser = ArgumentParser(prog='photometric_diagrams.py', description='>> Interactive \
CCD and CMD diagrams <<\n\n Requires Python 2.7 with:\n  * numpy\n  * argparse\n  * matplotlib\n\n',
epilog='Copyright (c) 2017 Przemysław Bruś', formatter_class=tefo)
argparser.add_argument('input_file', help='must contain columns with data and a one-line header\n\
The header must be preceded by # sign. Labels from the header \nwill be used to sign axes on charts')
argparser.add_argument('--col', help="columns which should be used to create \
the diagram\nA negative value reverses range's axis. There is no limit to the diagrams", \
nargs=2, dest='col', action='append', metavar=('col_x', 'col_y'), required=True, type=int)
argparser.add_argument('--grp', help='group of stars which can be marked by color\n\
/file/ should contain only one column with ID numbers of stars\nIf this option is used, \
also /input/ must have ID numbers of stars\nin the first column. The variable /color/ \
stores color which marks\nthe points from the /file/. The color can be specified \
by an html\nhex string ("#4f21b7") or literally (blue or b). For more details\nsee the \
matplotlib documentation. Gray and red colors are reserved\nfor plotting the background and \
selection of points, respectively', nargs=2, dest='grp', action='append', metavar=('file', 'color'))
argparser.add_argument('-t', help='talkative mode. Printing feedback with every click', \
action='store_true')
argparser.add_argument('-v', '--version', action='version', version='%(prog)s\n * Version: 2017-02-23\n \
* Licensed under the MIT license:\n   http://opensource.org/licenses/MIT\n * Copyright (c) 2017 Przemysław Bruś')
args = argparser.parse_args()

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

# get arguments
col = args.col
grp = args.grp
Nfig = len(col)
fl_grp = False
if grp != None:
    Ngrp = len(grp)
    fl_grp = True


# create tuples to store and to save the figure and ax for each window
fisave = ()
axsave = ()

figtup = get_figures(col, args.t)
axtup = tuple([fig.axes[0] for fig in figtup])

######################################################################################################

# save a diagram as inputfile_labelX_labelY_num.png, where num is a consecutive natural number
def save_diagram(fi, ax, rev, lab, bckgrd = (), mrkd = (), clrd = ()):
    if rev[0] < 0:
        fi.axes[0].invert_xaxis()
    if rev[1] < 0:
        fi.axes[0].invert_yaxis()

    ax.scatter(bckgrd[0], bckgrd[1], 60, c = background, alpha = 0.4, zorder = 1)
    if mrkd != ():
        ax.scatter(mrkd[0],mrkd[1], 100, c = marker, alpha = 1.0, zorder = 3)
    if clrd != ():
        for c in clrd:
            ax.scatter(c[0],c[1], 60, c = c[2], alpha = 0.6, zorder = 2)

    ax.set_title(lab[1] + " vs " + lab[0] + " diagram for " + str(N) + " stars", fontsize=20)
    ax.set_xlabel(lab[0] +  " [mag]", fontsize=15)
    ax.set_ylabel(lab[1] + " [mag]", fontsize=15)
    out = args.input_file + "_" + lab[1] + "_" + lab[0] + "_" + str(cnt_img) + ".png"
    fi.set_size_inches(10.0, 10.0, forward=True)
    fi.savefig(out)
    # important, close each figure avoiding program's freezing
    plt.close(fi)

# get coordinates of marked points
idevnt = []
def mark_pts(msk):
    global idevnt
    mrkd = ()
    if set(msk) != set(idevnt) or fl_save:
        for d in data:
            dat = d[-1]
            mrkpts = ()
            for m in msk:
                mrkpts += (dat[m],)
            mrkd += (mrkpts,)

        if args.t:
            feedback(msk)

        idevnt = msk
    else:
        idevnt = []

    return mrkd

# get coordinates of initially colored points
def clrd_pts(id_clr):
    clrdat = ()
    for i in range(Ngrp):
        idx = id_clr[i][0]
        color = id_clr[i][1]
        tmp1 = ()
        for d in data:
            tmp2 = ()
            dat = d[-1]
            for j in idx:
                tmp2 += (dat[j],)

            tmp1 += (tmp2,)
        tmp1 += (color,)
        clrdat += (tmp1,)

    return clrdat

# what to do when point is picked on
def onpick(event):
    msk = event.ind
    draw_all_figures(figtup,data,args.col,args.grp, mark_pts(msk),clrtup)

# connect all figures
def connect(fig):
    for fg in fig:
        fg.canvas.mpl_connect('pick_event', onpick)

# print the whole line of a marked point from the input file
def feedback(msk):
    for i,m in enumerate(msk):
        print("# object {}".format(i+1))
        for j in inpt[m]:
            print(j)

# save figures as images
cnt_img = 1
fl_save = False
def save_img():
    global fl_save,cnt_img,fisave,axsave
    for i in range(Nfig):
        fi = plt.figure()
        ax = fi.add_subplot(111)
        fisave += (fi,)
        axsave += (ax,)
    fl_save = True
    draw_all_figures(fisave,data,args.col,args.grp,mark_pts(idevnt),clrtup)
    fl_save = False
    cnt_img += 1
    fisave = ()
    axsave = ()

######################################################################################################

data = get_data(args.input_file, args.col)
clrtup = get_color_data(args.input_file, args.grp, data)

col_int = args.col
N = len(data[0][-1])

background = 'gray'
marker = 'red'

draw_all_figures(figtup,data,args.col, args.grp,colored_data=clrtup)

# make connections
connect(figtup)
plt.show()
