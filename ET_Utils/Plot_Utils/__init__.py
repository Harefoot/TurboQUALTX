import numpy as np
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
#import matplotlib.mlab as mlab    
import mpl_toolkits.axisartist as axisartist
from matplotlib import rcParams
    
def setup_page(outputpdf, pageorientation):    
   
    ###  Set up default parameters for matplotlib
    ###  rcParams are the default parameters for matplotlib
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['Century Gothic']
    rcParams['font.size'] = 10.
    rcParams['axes.labelsize'] = 10.
    rcParams['xtick.labelsize'] = 8.
    rcParams['ytick.labelsize'] = 12.

    if pageorientation == 'portrait':
        pagelength = 11
        pagewidth = 8.5
        
        #Set margins
        #top_mar = 0.95
        #bot_mar = 0.15
        #left_mar = 0.15
        #right_mar = 0.85
        #fig.subplots_adjust(bottom=bot_mar,top=top_mar,left=left_mar,right=right_mar)
        
    if pageorientation == 'landscape':
        pagelength = 8.5
        pagewidth = 11
        #top_mar = 0.95
        #bot_mar = 0.15
        #left_mar = 0.10
        #right_mar = 0.95
        
    fig = Figure(figsize=(pagewidth,pagelength))
    pp = PdfPages(outputpdf)

    # Create a canvas and add the figure to it.
    #canvas = FigureCanvas(fig)
    FigureCanvas(fig)
    #fig.subplots_adjust(bottom=bot_mar,top=top_mar,left=left_mar,right=right_mar)

    return fig, pp, axisartist

def next_page(pageorientation):    
   
    ###  Set up default parameters for matplotlib
    ###  rcParams are the default parameters for matplotlib
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['Century Gothic']
    rcParams['font.size'] = 10.
    rcParams['axes.labelsize'] = 10.
    rcParams['xtick.labelsize'] = 8.
    rcParams['ytick.labelsize'] = 12.

    if pageorientation == 'portrait':
        pagelength = 11
        pagewidth = 8.5
            #Set margins
        #top_mar = 0.95
        #bot_mar = 0.15
        #left_mar = 0.15
        #right_mar = 0.85
    
    if pageorientation == 'landscape':
        pagelength = 8.5
        pagewidth = 11
        #top_mar = 0.95
        #bot_mar = 0.15
        #left_mar = 0.10
        #right_mar = 0.95

    fig = Figure(figsize=(pagewidth,pagelength))
    #pp = PdfPages(outputpdf)

    # Create a canvas and add the figure to it.
    #canvas = FigureCanvas(fig)
    FigureCanvas(fig)
	
	#You can do margin adjustments in your main deck (no need to pass the margin variables)
    #fig.subplots_adjust(bottom=bot_mar,top=top_mar,left=left_mar,right=right_mar)

    return fig, axisartist
    
def setup_axes(ax, x_range, y_range, x_label, y_label, x_tickinterval = np.nan, y_tickinterval = np.nan, x_labelsize = 8, y_labelsize = 8):
    #More on keyword arguments https://docs.python.org/release/1.5.1p1/tut/keywordArgs.html
    
    ax.set_ylim(y_range)
    ax.set_xlim(x_range)
    # Set the X Axis label.
    ax.axis["bottom"].label.set_text(x_label)
    ax.axis["bottom"].label.set_weight('bold')
    ax.axis["bottom"].label.set_pad(15)  #specifies number of points between axis title and axis
    ax.axis["bottom"].label.set_size(x_labelsize)
    
    # Set the Y Axis label.
    ax.axis["left"].label.set_text(y_label)
    #ax.axis["left"].label.set_size(8)
    ax.axis["left"].label.set_size(y_labelsize)
    ax.axis["left"].label.set_weight('bold')
    ax.axis["left"].label.set_pad(7)
   
    #ax.tick_params(axis='both', which='major', labelsize=x_fontsize) 
    
    if np.isfinite(y_tickinterval):
        ax.set_yticks(range(y_range[0],y_range[1],y_tickinterval))

    if np.isfinite(x_tickinterval):
        ax.set_xticks(range(x_range[0],x_range[1],x_tickinterval))

def make_png(outputpdf, resolution = 100):    
    from wand.image import Image
    #For converting pdf to png (can't export natively in Matplotlib.  Matplotlib can only export pngs, jpgs, etc. one image at a time
    #for wand.image to work you need to install the ghostscript package (a la easy_install ghostscript)
    outputpng = ''.join(outputpdf.split('.')[0:-1])+'.png'
    with Image(filename=outputpdf,resolution = resolution) as img:         
        img.compression_quality = 99
        img.save(filename=outputpng)