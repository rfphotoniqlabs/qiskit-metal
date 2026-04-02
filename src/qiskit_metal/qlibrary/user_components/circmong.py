import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit
from shapely.geometry.base import CAP_STYLE
from shapely.geometry import Point


class CircmonG(BaseQubit):

    # Default drawing options
    default_options = Dict(
        pad_r='100um',
        pad2pk_gap='100um',
        jj_width='20um',
        jj_angle=0,
        fl_angle=90,
        jj_in_pad='2um',
        jj_in_pk='2um',
        l_fl=30,
        w_fl='10um',
        d_tsv='80um',
        g_tsv='10um',
        s_tsv='20um',
        cpads=Dict(),
        _default_cpads=Dict(
            cpw_width='10um',
            # pad_gap='15um',
            # south=False,
            # cpad_width='50um',
            # cpad_height='50um',
            # cpad2pad_gap='20um',
            # cpad2pk_gap='50um',
            # cpad_off='0um',
            # pad_width='20um',
            # pad_height='150um',
            # pad_cpw_extent='25um',
            # cpw_width='10um',
            # cpw_gap='6um',
            # position='nn'
        )
        # need to specify all lines' options when instantiating
        )

    def make(self):
        pad=Point(0,0).buffer(self.p.pad_r,resolution=32)
        pocket=Point(0,0).buffer(self.p.pad_r+self.p.pad2pk_gap,resolution=32)
        [pad,pocket]=self.make_jj(pad,pocket)
        self.make_cpads()
        [pad,pocket]=draw.rotate([pad,pocket],self.p.orientation,origin=(0, 0))
        [pad,pocket]=draw.translate([pad,pocket],self.p.pos_x,self.p.pos_y)
        # self.make_pocket()
        self.add_qgeometry('poly', dict(pad=pad))
        self.add_qgeometry('poly', dict(pocket=pocket), subtract=True)
        self.make_fl()

    def make_jj(self,pad,pocket):
        pad_r = self.p.pad_r
        pad2pk_gap = self.p.pad2pk_gap
        jj_width = self.p.jj_width
        # jj_pad=-np.sqrt(pad_r**2-(jj_width/2)**2)
        # jj_gp=-np.sqrt((pad_r+pad2pk_gap)**2-(jj_width/2)**2)
        jj_pad=pad_r-self.p.jj_in_pad
        jj_gp=pad_r+pad2pk_gap-self.p.jj_in_pk
        [rect_jj1,rect_jj2]=[draw.LineString([[jj_pad,0],[jj_gp,0]]),draw.LineString([[-jj_pad,0],[-jj_gp,0]])]
        [rect_jj1,rect_jj2]=draw.rotate([rect_jj1,rect_jj2],self.p.orientation+self.p.jj_angle,origin=(0, 0))
        [rect_jj1,rect_jj2]=draw.translate([rect_jj1,rect_jj2],self.p.pos_x,self.p.pos_y)
        self.add_qgeometry('junction',
                           dict(rect_jj1=rect_jj1,rect_jj2=rect_jj2),
                           width=self.p.jj_width
                           )
        padcut1=draw.LineString([[pad_r,-pad_r],[pad_r,pad_r]]).buffer(self.p.jj_in_pad,)
        padcut2=draw.LineString([[-pad_r,-pad_r],[-pad_r,pad_r]]).buffer(self.p.jj_in_pad,)
        [padcut1,padcut2]=draw.rotate([padcut1,padcut2],self.p.jj_angle,origin=(0, 0))
        pad=draw.subtract(pad,padcut1)
        pad=draw.subtract(pad,padcut2)
        pkcut1=draw.LineString([[pad_r+pad2pk_gap,-pad_r-pad2pk_gap],[pad_r+pad2pk_gap,pad_r+pad2pk_gap]]).buffer(self.p.jj_in_pk,)
        pkcut2=draw.LineString([[-pad_r-pad2pk_gap,-pad_r-pad2pk_gap],[-pad_r-pad2pk_gap,pad_r+pad2pk_gap]]).buffer(self.p.jj_in_pk,)
        [pkcut1,pkcut2]=draw.rotate([pkcut1,pkcut2],self.p.jj_angle,origin=(0, 0))
        pocket=draw.subtract(pocket,pkcut1)
        pocket=draw.subtract(pocket,pkcut2)
        return [pad,pocket]

    def make_cpads(self):
        for name in self.options.cpads:
            self.make_cpad(name)

    def make_cpad(self, name: str):
        p = self.p
        pc = self.p.cpads[name]

        # parse reused
        cpw_width = pc.cpw_width
        cpw_gap = pc.cpw_gap
        angle=pc.angle
        pad_r = p.pad_r
        pad2pk_gap = p.pad2pk_gap
        
        # Define the arc (presumably ezdxf uses a similar convention)
        centerx, centery = 0, 0
        radius = pad_r+pc.s+pc.w/2
        start_angle, end_angle = angle-pc.l/2, angle+pc.l/2 # In degrees
        numsegments = np.ceil(pc.l).astype(int)
        
        # The coordinates of the arc
        theta = np.radians(np.linspace(start_angle, end_angle, numsegments))
        x = centerx + radius * np.cos(theta)
        y = centery + radius * np.sin(theta)
        
        cpad=draw.LineString(np.column_stack([x, y])).buffer(pc.w/2,resolution=32,cap_style=CAP_STYLE.round)
        cpad_sub=cpad.buffer(pc.g,cap_style=CAP_STYLE.flat)
        line=draw.LineString([[(p.pad_r+pc.s+pc.w/2)*np.cos(np.radians(pc.angle)),(p.pad_r+pc.s+pc.w/2)*np.sin(np.radians(pc.angle))],
                             [(p.pad_r+pc.s+pc.w/2+pc.l_cpw)*np.cos(np.radians(pc.angle)),(p.pad_r+pc.s+pc.w/2+pc.l_cpw)*np.sin(np.radians(pc.angle))]])
        cpad=draw.union([cpad,line.buffer(pc.cpw_width/2,cap_style=CAP_STYLE.flat)])
        cpad_sub=draw.union([cpad_sub,line.buffer(pc.cpw_width/2+pc.cpw_gap,cap_style=CAP_STYLE.flat)])
        [cpad,cpad_sub,line]=draw.rotate([cpad,cpad_sub,line],self.p.orientation,origin=(0, 0))
        [cpad,cpad_sub,line]=draw.translate([cpad,cpad_sub,line],self.p.pos_x,self.p.pos_y)
        self.add_qgeometry('poly', {f'{name}': cpad})
        self.add_qgeometry('poly', {f'{name}_sub': cpad_sub},subtract=True)
        
        ############################################################

        # add pins
        points = np.array(line.coords)
        self.add_pin(name,
                     points=points,
                     width=cpw_width,
                     input_as_norm=True)
        
    def make_fl(self):
        p=self.p
        radius=p.pad_r+p.pad2pk_gap+p.g_tsv+p.d_tsv/2+p.s_tsv
        theta1 = np.radians(np.linspace(p.l_fl/2, -p.l_fl/2, np.ceil(p.l_fl).astype(int)))
        x1 = radius * np.cos(theta1)
        y1 = radius * np.sin(theta1)
        fl1=draw.LineString(np.column_stack([x1,y1])).buffer(p.w_fl/2,resolution=32,cap_style=CAP_STYLE.round)
        fl1=draw.union([fl1,Point(radius*np.cos(np.radians(p.l_fl/2)),radius*np.sin(np.radians(p.l_fl/2))).buffer(p.d_tsv/2,resolution=32)])
        fl1=draw.union([fl1,Point(radius*np.cos(np.radians(-p.l_fl/2)),radius*np.sin(np.radians(-p.l_fl/2))).buffer(p.d_tsv/2,resolution=32)])
        fl1_sub=draw.LineString(np.column_stack([x1,y1])).buffer(p.d_tsv/2+p.g_tsv,resolution=32,cap_style=CAP_STYLE.round)
        theta2 = np.radians(np.linspace(p.l_fl/2+180, -p.l_fl/2+180, np.ceil(p.l_fl).astype(int)))
        x2 = radius * np.cos(theta2)
        y2 = radius * np.sin(theta2)
        fl2=draw.LineString(np.column_stack([x2,y2])).buffer(p.w_fl/2,resolution=32,cap_style=CAP_STYLE.round)
        fl2=draw.union([fl2,Point(radius*np.cos(np.radians(p.l_fl/2+180)),radius*np.sin(np.radians(p.l_fl/2+180))).buffer(p.d_tsv/2,resolution=32)])
        fl2=draw.union([fl2,Point(radius*np.cos(np.radians(-p.l_fl/2+180)),radius*np.sin(np.radians(-p.l_fl/2+180))).buffer(p.d_tsv/2,resolution=32)])
        fl2_sub=draw.LineString(np.column_stack([x2,y2])).buffer(p.d_tsv/2+p.g_tsv,resolution=32,cap_style=CAP_STYLE.round)
        [fl1,fl1_sub,fl2,fl2_sub]=draw.rotate([fl1,fl1_sub,fl2,fl2_sub],self.p.orientation+self.p.fl_angle,origin=(0, 0))
        [fl1,fl1_sub,fl2,fl2_sub]=draw.translate([fl1,fl1_sub,fl2,fl2_sub],self.p.pos_x,self.p.pos_y)
        self.add_qgeometry('poly', dict(fl1=fl1,fl2=fl2))
        self.add_qgeometry('poly', dict(fl1_sub=fl1_sub,fl2_sub=fl2_sub),subtract=True)