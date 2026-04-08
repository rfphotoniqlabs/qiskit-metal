#spr_box_create
#Qubit must be at origin and unrotated
#So far doesn't support connectors

# -- Helpers: set CreateBox parameters via HFSS COM modeler -------------------
def _set_box_prop(design, obj_name, prop_path, value):
    """Set a property on CreateBox:1 child of an HFSS object via COM."""
    design.renderers.hfss.modeler._modeler \
        .GetChildObject(obj_name) \
        .GetChildObject('CreateBox:1') \
        .SetPropValue(prop_path, value)

def _set_obj_prop(design, obj_name, prop, value):
    """Set a top-level property on an HFSS object via COM."""
    design.renderers.hfss.modeler._modeler \
        .GetChildObject(obj_name) \
        .SetPropValue(prop, value)

def _draw_spr_box(design, name, x0, y0, xs, ys, thickness):
    """
    Draw a thin (nm-scale) non-model box centred at z=0 for SPR integration.

    Parameters
    ----------
    x0, y0     : str  Lower-left corner (HFSS parametric expressions)
    xs, ys     : str  XY dimensions
    thickness  : str  Z-dimension (box is centred at z=0)
    """
    modeler = design.renderers.hfss.modeler
    modeler.draw_box_center([0, 0, 0], [1e-3, 1e-3, 1e-3], name=name)
    _set_obj_prop(design, name, 'Model', False)          # non-model
    _set_box_prop(design, name, 'ZSize',      thickness)
    _set_box_prop(design, name, 'Position/Z', f'-({thickness})/2')
    _set_box_prop(design, name, 'XSize',      xs)
    _set_box_prop(design, name, 'Position/X', x0)
    _set_box_prop(design, name, 'YSize',      ys)
    _set_box_prop(design, name, 'Position/Y', y0)
    return name
