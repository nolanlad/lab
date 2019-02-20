from matplotlib import pyplot as plt
import numpy as np
from copy import copy
import json
import glob

class LineBuilder:
    def __init__(self, line):
        self.line = line
        self.even = False
        self.line_list = []
        self._line = Line()
        self.count = 0
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
        

    def __call__(self, event):
        if event.inaxes!=self.line.axes: return
        if(event.key == 'shift'):
            print("zoom")
            return
        if self.even:
            self._line.x2 = event.xdata
            self._line.y2 = event.ydata
            
            self.line.set_data([self._line.x1,self._line.x2] ,
                               [self._line.y1, self._line.y2])
            self._line.id = self.count
            self.count += 1
            self.line_list.append(copy(self._line))
            self.line.figure.canvas.draw()
        else:
            self._line.x1 = event.xdata
            self._line.y1 = event.ydata
        self.even = (not self.even)

class Line:
    def __init__(self, x1=None, y1=None, x2=None, y2=None):
        self.id = None
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def length(self,x_scale,y_scale):
        self.length = get_length([self.x1,self.x2],
                                 [self.y1,self.y2],
                                 x_scale,y_scale)
    

def draw_lines(img,prefix):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    v = plt.imread(img)
    ax.imshow(v)
    line, = ax.plot([], [])  # empty line
    linebuilder = LineBuilder(line)

    plt.show()
    info = read_hdr(img.replace(".tif","-tif.hdr"))
    xscale,yscale = float(info['PixelSizeX']),float(info['PixelSizeY'])
    line_list = linebuilder.line_list
    for i in line_list:
        i.length(xscale,yscale)
    fp = open(img+prefix+".json",'a')
    json.dump([i.__dict__ for i in line_list],fp)
    #return line_list

def test_lines(img,prefix):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    v = plt.imread(img)
    ax.imshow(v)
    line, = ax.plot([], [])  # empty line
    linebuilder = LineBuilder(line)

    plt.show()
    

def get_length(xs,ys,x_scale,y_scale):
    dx = xs[0] - xs[1]
    dy = ys[0] - ys[1]
    dx = dx*x_scale
    dy = dy*y_scale
    return np.sqrt(dx**2 + dy**2)

def read_hdr(fname):
    f = open(fname)
    lines = f.read().split('\n')
    keys =  {}
    for line in lines:
        if "=" in line:
            temp = line.split("=")
            keys[temp[0]] = temp[1]
    return keys

def draw_with_lines(img,prefix,files):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    v = plt.imread(img)
    ax.imshow(v)
    lines = []
    for f in files:
        dump = json.load(open(f))
        for j in dump:
            x1 = j['x1']
            x2 = j['x2']
            y1 = j['y1']
            y2 = j['y2']
            plt.plot([x1,x2],[y1,y2],'b-')
            
    line, = ax.plot([], [])  # empty line
    linebuilder = LineBuilder(line)

    plt.show()
    info = read_hdr(img.replace(".tif","-tif.hdr"))
    xscale,yscale = float(info['PixelSizeX']),float(info['PixelSizeY'])
    line_list = linebuilder.line_list
    for i in line_list:
        i.length(xscale,yscale)
    fp = open(img+"."+prefix+".json",'a')
    print(img+"."+prefix+".json")
    json.dump([i.__dict__ for i in line_list],fp)
    return line_list

def all_files(pattern):
    v = []
    for d in dirs:
        v.extend(glob.glob("/home/nolan/Desktop/101018_HNS_2-4/%s/%s"%(d,pattern)))
    return v

def main(crack_number):
    fils = all_files("panorama.tif.crack[0-9].json")
    #dirs.reverse()
    for d in dirs:
        fils = all_files("panorama.tif.crack[0-9].json")
        draw_with_lines("/home/nolan/Desktop/101018_HNS_2-4/%s/panorama.tif"%(d),"crack%d"%(crack_number), fils)
        if(input() == 'q'):
            break

def get_crack_length(files):
    points = []
    for f in files:
        data = json.load(open(f))
        if data != []:
            points.append(
                np.average(
                    [d['length'] for d in data]))
    return points

def show_all_crack(files,pattern):
    for f in files:
        im = plt.imread(f.replace(pattern,".tif"))
        plt.imshow(im)
        dump = json.load(open(f))
        for j in dump:
            x1 = j['x1']
            x2 = j['x2']
            y1 = j['y1']
            y2 = j['y2']
            plt.plot([x1,x2],[y1,y2],'b-')
        plt.show()
        
        

dirs = ['0N', '41N','61N','78N','99N','118N','139N','170N','190N','Failure']
dirs.reverse()
