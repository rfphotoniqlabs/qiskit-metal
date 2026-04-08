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
def create_circmong_spr_boxes(design, q):
    """
    Create three thin EPR reference boxes for SPR surface-loss analysis.

    Boxes (all centred at origin, z-centred at z=0):
      1. MA_island_{q.name}  Metal-Air on qubit island
                             Square side = 2*pad_r, thickness = 5 nm
      2. SDA_slot_{q.name}   Substrate-Air in the annular slot
                             Square side = 2*(pad_r+gap), thickness = 3 nm
                             (island area subtracted analytically in Step 8b)
      3. MA_ground_{q.name}  Metal-Air near-qubit ground plane
                             Square side = 4*(pad_r+gap), thickness = 5 nm
                             (slot+island subtracted analytically in Step 8b)

    Returns
    -------
    dict  {interface_key: HFSS_object_name}
    """
    pad_r = q.options.pad_r       # e.g. '200um'
    gap   = q.options.pad2pk_gap  # e.g. '100um'

    t_MA  = '5um'
    t_SDA = '5um'

    boxes = {}
    '''
    # 1. MA_island
    name = f'MA_island_{q.name}'
    _draw_spr_box(design, name,
                  x0=f'-({pad_r})',  y0=f'-({pad_r})',
                  xs=f'2*({pad_r})', ys=f'2*({pad_r})',
                  thickness=t_MA)
    boxes['MA_island'] = name
    print(f'  [OK] {name:28s}  XY=2x{pad_r}  t={t_MA}')

    # 2. SDA_slot
    R_out_expr = f'({pad_r}+{gap})'
    name = f'SDA_slot_{q.name}'
    _draw_spr_box(design, name,
                  x0=f'-{R_out_expr}',  y0=f'-{R_out_expr}',
                  xs=f'2*{R_out_expr}', ys=f'2*{R_out_expr}',
                  thickness=t_SDA)
    boxes['SDA_slot'] = name
    print(f'  [OK] {name:28s}  XY=2x({pad_r}+{gap})  t={t_SDA}')
    '''
    # 3. MA_ground
    R_gnd_expr = f'2*({pad_r}+{gap})'
    name = f'MA_ground_{q.name}'
    _draw_spr_box(design, name,
                  x0=f'-{R_gnd_expr}',  y0=f'-{R_gnd_expr}',
                  xs=f'2*{R_gnd_expr}', ys=f'2*{R_gnd_expr}',
                  thickness=t_MA)
    boxes['MA_ground'] = name
    print(f'  [OK] {name:28s}  XY=4x({pad_r}+{gap})  t={t_MA}')

    return boxes
