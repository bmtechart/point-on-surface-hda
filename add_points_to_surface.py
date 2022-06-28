import hou
import viewerstate.utils as su


class State(object):
    MSG = "LMB to add points to the surface of mesh."

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self.pressed = False
        self.index = 0    
        self.node = None
        self._geometry = None


    def pointCount(self):
        """ This is how you get the number of instances 
            in a multiparm. 
        """
        try:
            multiparm = self.node.parm("points")
            return multiparm.evalAsInt()
        except:
            return 0

    def start(self):
        #increment index value
        if not self.pressed:
            self.scene_viewer.beginStateUndo("Add point")
            self.index = self.pointCount()
            multiparm = self.node.parm("points")
            multiparm.insertMultiParmInstance(self.index)

        self.pressed = True

    def finish(self):
        if self.pressed:
            self.scene_viewer.endStateUndo()
        self.pressed = False

    def onEnter(self, kwargs):
        self.node = kwargs["node"]
        self._message = "Click to add points to surface."

        #show display geometry
        


        if not self.node:
            raise
        
        inputs = self.node.inputs()
        
        if inputs and inputs[0]:
            self._geometry = inputs[0].geometry()

        self.display_geo = self.node.node("VIEWER_STATE_COLLISION_GEO").geometry()
        self.drawable = hou.SimpleDrawable(self.scene_viewer, self.display_geo, "point_collision_surface")
        self.drawable.setDisplayMode(hou.drawableDisplayMode.CurrentViewportMode)

        self.drawable.enable(True)
        self.drawable.show(True)

        self.scene_viewer.setPromptMessage( self._message )

    def onInterrupt(self,kwargs):
        self.finish()

    def onResume(self, kwargs):
        self.scene_viewer.setPromptMessage( self._message )
    
    def onMouseEvent(self, kwargs):
        """ Find the position of the point to add by 
            intersecting the construction plane. 
        """
        ui_event = kwargs["ui_event"]
        device = ui_event.device()
        origin, direction = ui_event.ray()
        
        
        
        if self._geometry:
            hit, pos, norm, uvw = sopGeometryIntersection(
                self._geometry, origin, direction
            )

        position = pos

        if hit != -1:   
            # Create/move point if LMB is down
            if device.isLeftButton():
                self.start()
                # set the point position
                self.node.parm("usept%d" % self.index).set(1)
                self.node.parmTuple("pt%d" % self.index).set(position)
                
            else:
                self.finish()
            
        return True

def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "addpointstosurface"
    state_label = "Points On Surface"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    #template.bindIcon(kwargs["type"].icon())

    return template

def sopGeometryIntersection(geometry, ray_origin, ray_dir):
    # Make objects for the intersect() method to modify
    
    position = hou.Vector3()
    normal = hou.Vector3()
    uvw = hou.Vector3()
    # Try intersecting the ray with the geometry
    intersected = geometry.intersect(
        ray_origin, ray_dir, position, normal, uvw
    )
    # Returns a tuple of four values:
    # - the primitive number of the primitive hit, or -1 if the ray didn't hit
    # - the 3D position of the intersection point (as Vector3)
    # - the normal of the ray to the hit primitive (as Vector3)
    # - the uvw coordinates of the intersection on the primitive (as Vector3)
    return intersected, position, normal, uvw
