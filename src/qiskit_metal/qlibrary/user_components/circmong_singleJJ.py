import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit
from shapely.geometry import Point


class CircmonG(BaseQubit):
    """Grounded circular transmon — single Josephson Junction.

    Geometry
    --------
    pad      : filled circle of radius ``pad_r``.
               The floating qubit island.
    pocket   : annular ring of radial width ``pad2pk_gap``,
               subtracted from the ground plane.
               Together with the pad, it defines the transmon capacitance.
    rect_jj1 : single Josephson Junction bridging the pocket at the angle
               set by ``jj_angle`` (default 0 deg → east, +x direction).
               The JJ line runs from the pad edge inward by ``jj_in_pad``
               to the outer pocket edge inward by ``jj_in_pk``.

    Removed from original design
    ----------------------------
    * TSV coupler arcs  (``make_fl``, ``fl1`` / ``fl2``)
    * Coupling / drive pads with CPW lines and pins  (``make_cpads`` / ``make_cpad``)
    * Second Josephson Junction  (``rect_jj2``, ``padcut2``, ``pkcut2``)
    * Associated options: ``fl_angle``, ``l_fl``, ``w_fl``, ``d_tsv``,
      ``g_tsv``, ``s_tsv``, ``cpads``, ``_default_cpads``

    Options
    -------
    pad_r       : radius of the central metallic disk (qubit island).
    pad2pk_gap  : radial width of the annular slot in the ground plane.
    jj_width    : width of the single JJ bridge element.
    jj_angle    : azimuthal angle of the JJ in degrees (0 = east / +x).
    jj_in_pad   : how far the JJ line overlaps into the pad edge.
    jj_in_pk    : how far the JJ line overlaps into the pocket outer edge.
    """

    default_options = Dict(
        pad_r      = '100um',
        pad2pk_gap = '100um',
        jj_width   = '20um',
        jj_angle   = 0,       # degrees; 0 = east (+x), 90 = north (+y), etc.
        jj_in_pad  = '2um',
        jj_in_pk   = '2um',
        hfss_inductance = 'Lj',  
        hfss_capacitance= 'Cj',
    )

    def make(self):
        # ── 1. Build pad (disk) and pocket (annular slot) ──────────────────
        pad    = Point(0, 0).buffer(self.p.pad_r,                        resolution=32)
        pocket = Point(0, 0).buffer(self.p.pad_r + self.p.pad2pk_gap,   resolution=32)

        # ── 2. Add the single JJ; returns notched pad and pocket ───────────
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
        """Create a single JJ and the matching notches in pad and pocket.

        The JJ line runs radially from (pad_r - jj_in_pad) to
        (pad_r + pad2pk_gap - jj_in_pk) at azimuthal angle ``jj_angle``.
        A rectangular notch is cut from the pad at the JJ position, and a
        matching notch from the pocket, so the JJ is the only metal bridge
        crossing the slot.

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
        jj_pad = pad_r      - self.p.jj_in_pad   # inner end (inside pad edge)
        jj_gp  = pad_r + pad2pk_gap - self.p.jj_in_pk  # outer end (inside pocket edge)

        # ── Single JJ geometry ────────────────────────────────────────────
        rect_jj1 = draw.LineString([[jj_pad, 0], [jj_gp, 0]])

        # Apply jj_angle + component orientation, then translate to world frame
        rect_jj1 = draw.rotate(
            rect_jj1, self.p.orientation + self.p.jj_angle, origin=(0, 0))
        rect_jj1 = draw.translate(rect_jj1, self.p.pos_x, self.p.pos_y)

        self.add_qgeometry(
            'junction',
            dict(rect_jj1=rect_jj1),
            width=self.p.jj_width,
            hfss_inductance  = self.p.hfss_inductance,   # 'Lj' → parametric
            hfss_capacitance = self.p.hfss_capacitance,  # 'Cj' → parametric
        )

        # ── Notch in the pad at the JJ position ───────────────────────────
        # A tall vertical buffer centred on the pad edge at +x, rotated by
        # jj_angle, then subtracted from the pad (local frame).
        padcut = (draw.LineString([[pad_r, -pad_r], [pad_r, pad_r]])
                  .buffer(self.p.jj_in_pad))
        padcut = draw.rotate(padcut, self.p.jj_angle, origin=(0, 0))
        pad    = draw.subtract(pad, padcut)

        # ── Notch in the pocket at the JJ position ────────────────────────
        pkcut  = (draw.LineString(
                      [[pad_r + pad2pk_gap, -(pad_r + pad2pk_gap)],
                       [pad_r + pad2pk_gap,   pad_r + pad2pk_gap]])
                  .buffer(self.p.jj_in_pk))
        pkcut  = draw.rotate(pkcut, self.p.jj_angle, origin=(0, 0))
        pocket = draw.subtract(pocket, pkcut)

        return pad, pocket