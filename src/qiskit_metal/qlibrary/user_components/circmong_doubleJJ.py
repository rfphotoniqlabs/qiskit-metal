import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit
from shapely.geometry import Point


class CircmonG(BaseQubit):
    """Grounded circular transmon — dual Josephson Junction.

    Geometry
    --------
    pad      : filled circle of radius ``pad_r``.
               The floating qubit island.
    pocket   : annular ring of radial width ``pad2pk_gap``,
               subtracted from the ground plane.
               Together with the pad, it defines the transmon capacitance.
    rect_jj1 : first Josephson Junction bridging the pocket at the angle
               set by ``jj_angle`` (default 0 deg → east, +x direction).
               The JJ line runs from the pad edge inward by ``jj_in_pad``
               to the outer pocket edge inward by ``jj_in_pk``.
    rect_jj2 : second Josephson Junction at ``jj_angle + jj_offset_angle``.
               Uses the same geometry as rect_jj1.

    Removed from original design
    ----------------------------
    * TSV coupler arcs  (``make_fl``, ``fl1`` / ``fl2``)
    * Coupling / drive pads with CPW lines and pins  (``make_cpads`` / ``make_cpad``)
    * Associated options: ``fl_angle``, ``l_fl``, ``w_fl``, ``d_tsv``,
      ``g_tsv``, ``s_tsv``, ``cpads``, ``_default_cpads``

    Options
    -------
    pad_r           : radius of the central metallic disk (qubit island).
    pad2pk_gap      : radial width of the annular slot in the ground plane.
    jj_width        : width of each JJ bridge element.
    jj_angle        : azimuthal angle of the first JJ in degrees (0 = east / +x).
    jj_offset_angle : angular offset of the second JJ from the first (degrees).
    jj_in_pad       : how far the JJ line overlaps into the pad edge.
    jj_in_pk        : how far the JJ line overlaps into the pocket outer edge.
    """

    default_options = Dict(
        pad_r           = '100um',
        pad2pk_gap      = '100um',
        jj_width        = '20um',
        jj_angle        = 0,    # degrees; 0 = east (+x), 90 = north (+y), etc.
        jj_offset_angle = 180,  # degrees offset of second JJ from first JJ
        jj_in_pad       = '2um',
        jj_in_pk        = '2um',
        hfss_inductance_jj1  = 'Lj1',   
        hfss_inductance_jj2  = 'Lj2',   
        hfss_capacitance_jj1 = 'Cj',    
        hfss_capacitance_jj2 = 'Cj',
    )

    def make(self):
        # ── 1. Build pad (disk) and pocket (annular slot) ──────────────────
        pad    = Point(0, 0).buffer(self.p.pad_r,                        resolution=32)
        pocket = Point(0, 0).buffer(self.p.pad_r + self.p.pad2pk_gap,   resolution=32)

        # ── 2. Add both JJs; returns notched pad and pocket ────────────────
        pad, pocket = self.make_jj(pad, pocket)

        # ── 3. Apply component-level rotation and translation ──────────────
        pad, pocket = draw.rotate(
            [pad, pocket], self.p.orientation, origin=(0, 0))
        pad, pocket = draw.translate(
            [pad, pocket], self.p.pos_x, self.p.pos_y)

        # ── 4. Register geometries ─────────────────────────────────────────
        self.add_qgeometry('poly', dict(pad=pad))
        self.add_qgeometry('poly', dict(pocket=pocket), subtract=True)

    # ──────────────────────────────────────────────────────────────────────
    def make_jj(self, pad, pocket):
        """Create two JJs and the matching notches in pad and pocket.

        rect_jj1 sits at ``jj_angle``; rect_jj2 sits at
        ``jj_angle + jj_offset_angle``.  Both share the same radial extent
        and width.

        Parameters
        ----------
        pad    : shapely Polygon — circular qubit island (local frame)
        pocket : shapely Polygon — annular pocket (local frame)

        Returns
        -------
        [pad, pocket] : notched versions, still in local frame
        """
        pad_r      = self.p.pad_r
        pad2pk_gap = self.p.pad2pk_gap

        # JJ line endpoints (in local frame, before jj_angle rotation)
        jj_pad = pad_r           - self.p.jj_in_pad   # inner end (inside pad edge)
        jj_gp  = pad_r + pad2pk_gap - self.p.jj_in_pk  # outer end (inside pocket edge)

        # ── First JJ geometry ─────────────────────────────────────────────
        rect_jj1 = draw.LineString([[jj_pad, 0], [jj_gp, 0]])

        # Apply jj_angle + component orientation, then translate to world frame
        rect_jj1 = draw.rotate(
            rect_jj1, self.p.orientation + self.p.jj_angle, origin=(0, 0))
        rect_jj1 = draw.translate(rect_jj1, self.p.pos_x, self.p.pos_y)

        self.add_qgeometry(
            'junction',
            dict(rect_jj1=rect_jj1),
            width=self.p.jj_width,
            hfss_inductance  = self.p.hfss_inductance_jj1,   # 'Lj1'
            hfss_capacitance = self.p.hfss_capacitance_jj1,  # 'Cj'
        )

        # ── Second JJ geometry ────────────────────────────────────────────
        rect_jj2 = draw.LineString([[jj_pad, 0], [jj_gp, 0]])

        # Apply (jj_angle + jj_offset_angle) + component orientation, then translate
        rect_jj2 = draw.rotate(
            rect_jj2,
            self.p.orientation + self.p.jj_angle + self.p.jj_offset_angle,
            origin=(0, 0))
        rect_jj2 = draw.translate(rect_jj2, self.p.pos_x, self.p.pos_y)

        self.add_qgeometry(
            'junction',
            dict(rect_jj2=rect_jj2),
            width=self.p.jj_width,
            hfss_inductance  = self.p.hfss_inductance_jj2,   # 'Lj2'
            hfss_capacitance = self.p.hfss_capacitance_jj2,  # 'Cj'
        )

        # ── Notch in the pad at JJ1 position ──────────────────────────────
        padcut = (draw.LineString([[pad_r, -pad_r], [pad_r, pad_r]])
                  .buffer(self.p.jj_in_pad))
        padcut = draw.rotate(padcut, self.p.jj_angle, origin=(0, 0))
        pad    = draw.subtract(pad, padcut)

        # ── Notch in the pocket at JJ1 position ───────────────────────────
        pkcut  = (draw.LineString(
                      [[pad_r + pad2pk_gap, -(pad_r + pad2pk_gap)],
                       [pad_r + pad2pk_gap,   pad_r + pad2pk_gap]])
                  .buffer(self.p.jj_in_pk))
        pkcut  = draw.rotate(pkcut, self.p.jj_angle, origin=(0, 0))
        pocket = draw.subtract(pocket, pkcut)

        # ── Notch in the pad at JJ2 position ──────────────────────────────
        padcut2 = (draw.LineString([[pad_r, -pad_r], [pad_r, pad_r]])
                   .buffer(self.p.jj_in_pad))
        padcut2 = draw.rotate(
            padcut2, self.p.jj_angle + self.p.jj_offset_angle, origin=(0, 0))
        pad     = draw.subtract(pad, padcut2)

        # ── Notch in the pocket at JJ2 position ───────────────────────────
        pkcut2  = (draw.LineString(
                       [[pad_r + pad2pk_gap, -(pad_r + pad2pk_gap)],
                        [pad_r + pad2pk_gap,   pad_r + pad2pk_gap]])
                   .buffer(self.p.jj_in_pk))
        pkcut2  = draw.rotate(
            pkcut2, self.p.jj_angle + self.p.jj_offset_angle, origin=(0, 0))
        pocket  = draw.subtract(pocket, pkcut2)

        return pad, pocket