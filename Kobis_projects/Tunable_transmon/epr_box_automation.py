#EPR Box Automation
#Qubit must be at origin and unrotated
#So far doesn't support connectors
def create_epr_box(design,q,thickness,pocket_buffer):
    name=f'epr_box_{q.name}'
    design.renderers.hfss.modeler.draw_box_center([0,0,0],[1e-3,1e-3,1e-3],name=name)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).SetPropValue('Model',False)
    set_epr_box_thickness(design,name,thickness)
    set_epr_box_pocket_buffer(design,q,name,pocket_buffer)

def resize_epr_box(q,name,**kwargs):
    if 'thickness' in kwargs:
        thickness=kwargs['thickness']
        set_epr_box_thickness(name,thickness)
    if 'pocket_buffer' in kwargs:
        pocket_buffer=kwargs['pocket_buffer']
        set_epr_box_pocket_buffer(q,name,pocket_buffer)

def set_epr_box_thickness(design,name,thickness):
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('ZSize',thickness)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Z',f'-{thickness}/2')

def set_epr_box_pocket_buffer(design,q,name,pocket_buffer):
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('XSize',q.options.pad_width+'+'+q.options.pad_height+'+2*('+pocket_buffer+')+2*'+q.options.pad2pk_gap)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/X','-'+q.options.pad_width+'/2-'+q.options.pad_height+'/2-('+pocket_buffer+')-'+q.options.pad2pk_gap)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('YSize',q.options.pad_gap+'+2*'+q.options.pad_height+'+2*('+pocket_buffer+')+2*'+q.options.pad2pk_gap)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Y','-'+q.options.pad_gap+'/2-'+q.options.pad_height+'-('+pocket_buffer+')-'+q.options.pad2pk_gap)
    
def create_pads_epr_box(design,q,thickness):
    name=f'pads_epr_box_{q.name}'
    design.renderers.hfss.modeler.draw_box_center([0,0,0],[1e-3,1e-3,1e-3],name=name)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).SetPropValue('Model',False)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('ZSize',thickness)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Z',f'-{thickness}/2')
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('XSize',q.options.pad_width+'+'+q.options.pad_height)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/X','-'+q.options.pad_width+'/2-'+q.options.pad_height+'/2')
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('YSize',q.options.pad_gap+'+2*'+q.options.pad_height)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Y','-'+q.options.pad_gap+'/2-'+q.options.pad_height)
    
def create_gap_epr_box(design,q,thickness):
    name=f'gap_epr_box_{q.name}'
    design.renderers.hfss.modeler.draw_box_center([0,0,0],[1e-3,1e-3,1e-3],name=name)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).SetPropValue('Model',False)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('ZSize',thickness)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Z',f'-{thickness}/2')
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('XSize',q.options.pad_width)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/X','-'+q.options.pad_width+'/2')
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('YSize',q.options.pad_gap)
    design.renderers.hfss.modeler._modeler.GetChildObject(name).GetChildObject('CreateBox:1').SetPropValue('Position/Y','-'+q.options.pad_gap+'/2')