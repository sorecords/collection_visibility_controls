# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#  COLLECTION VISIBILITY CONTROLS
#  Control Collections visibility with Empty objects visibility 
#  (c) 2020 Andrey Sokolov (so_records)

bl_info = {
    "name": "Collection Visibility Controls",
    "author": "Andrey Sokolov",
    "version": (1, 0, 0),
    "blender": (2, 83, 3),
    "location": "Render Settings > Collection Visibility Controls",
    "description": "Control Collections visibility with Empty objects visibility",
    "warning": "",
    "wiki_url": "https://github.com/sorecords/collection_visibility_controls/blob/master/README.md",
    "tracker_url": "https://github.com/sorecords/collection_visibility_controls/issues",
    "category": "Render"
}

import bpy
from bpy.types import Operator, Panel, Menu, PropertyGroup
from bpy.props import BoolProperty, PointerProperty
from bpy.utils import register_class, unregister_class

# Common helper functions

def getcols(parent):
    if not len(parent.children):
        return []
    cols = []
    for child in parent.children:
        cols.append(child)
        other = getcols(child)
        if other:
            cols+=other
    return cols

def getname(col):
    return f'{col.name}.visibility.cntrl'

def getfcurvevalue(obj, data_path, frame):
    ad = obj.animation_data
    if not ad or not ad.action or not len(ad.action.fcurves):
        return None
    fc = [f for f in ad.action.fcurves if f.data_path==data_path]
    return fc[0].evaluate(frame) if fc else None

def setup_prop(col, obj, prop):
    fr = bpy.context.scene.frame_current_final
    value = getfcurvevalue(obj, prop, fr)
    res = getattr(obj,prop) if value is None else value
    if getattr(col,prop) != res:
        setattr(col,prop,res)

def setup_collection(col, obj):
    cntrl = bpy.context.scene.colcntrl
    if cntrl.render:
        setup_prop(col, obj, 'hide_render')
    if cntrl.viewport:
        setup_prop(col, obj, 'hide_viewport')
    if cntrl.select:
        setup_prop(col, obj, 'hide_select')

#frame_change_pre handler function

def collection_controls(self, context):
    sc = bpy.context.scene
    if not sc.colcntrl.activate:
        return
    for col in getcols(sc.collection):
        name = getname(col)
        if not name in col.objects:
            continue
        setup_collection(col, col.objects[name])
    sc.update_tag()

# Property Group

class ColCntrlProps(PropertyGroup):
    activate : BoolProperty(
        name="",
        description="Hide Collection from Render",
        default=False
    )
    render : BoolProperty(
        name="Render",
        description="Affect render visibility",
        default = True
    )
    viewport : BoolProperty(
        name="Viewport",
        description="Affect viewport visibility",
        default = True
    )
    select : BoolProperty(
        name="Select",
        description="Affect select visibility",
        default = True
    )

# Setup Operator

class ColHideRenderSetup(Operator):
    bl_idname = "colcntrl.setup"
    bl_label = "Controllers Setup"
    
    def newobj(self, name):
        return ( bpy.data.objects[name] if name in bpy.data.objects
                            else bpy.data.objects.new(name, None) )
    
    def obj_to_col(self, obj, col):
        for cl in bpy.data.collections:
            if obj.name in cl.objects:
                cl.objects.unlink(obj)
        obj.hide_render = col.hide_render
        obj.hide_viewport = col.hide_viewport
        obj.hide_select = col.hide_select
        obj.scale = [0,0,0]
        col.objects.link(obj)
        
    def colsetup(self, col):
        name = getname(col)
        self.obj_to_col(self.newobj(name),col)
    
    def execute(self, context):
        while collection_controls in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(collection_controls)
        for col in getcols(context.scene.collection):
            self.colsetup(col)
        bpy.app.handlers.frame_change_pre.append(collection_controls)
        return {'FINISHED'}

# UI

class COLCNTRL_PT_hiderender(Panel):
    bl_label = "Collection Visibility Controls"
    bl_idname = "COLCNTRL_PT_hiderender"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "render"
    bl_category = 'add-on'
    
    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.colcntrl
        col = layout.column()
        col.prop(props, "activate")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.colcntrl
        layout.active = props.activate
        
        layout.operator("colcntrl.setup")
        sep = layout.split(align = True)
        ren = sep.prop(props, "render",icon = 'RESTRICT_RENDER_OFF')
        sep.prop(props, "viewport", icon = 'RESTRICT_VIEW_OFF')
        sep.prop(props, "select", icon = 'RESTRICT_SELECT_OFF')

# execute on load

def execonload(self, context):
    scene = bpy.context.scene
    for sc in bpy.data.scenes:
        if sc.colcntrl.activate:
            bpy.context.window.scene = sc
            bpy.ops.colcntrl.setup()
    bpy.context.window.scene = scene
        

classes = [
    ColCntrlProps,
    ColHideRenderSetup,
    COLCNTRL_PT_hiderender
]

def register():
    for cl in classes:
        register_class(cl)
    bpy.types.Scene.colcntrl = PointerProperty(type=ColCntrlProps)
    bpy.app.handlers.persistent(execonload)
    bpy.app.handlers.load_post.append(execonload)

def unregister():
    while execonload in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(execonload)
    while collection_controls in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(collection_controls)
    for cl in reversed(classes):
        unregister_class(cl)
        
# Test
if __name__ == '__main__':
    register()