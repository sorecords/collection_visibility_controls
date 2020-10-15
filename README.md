# Collection Visibility Controls
# Blender 2.8+ add-on to control collections visibility

# FUNCTION
* Creates Empty objects for each Collection in the scene to control collection visibility (render, viewport and select) with its Empty object's visibility
* Checks changes on every frame change
* Allows you to keyframe collection visibility by keyframing Empty's visibility *(by default collection visibility keyframing in Blender is blocked)

# WARNING
* This is a kind of hack out Blender render system, so in some cases it may cause crashes while rendering animation. Use with caution, at your own risk.

# INSTALL:
* Download ZIP file
* Open Blender -> Top Menu -> Edit -> Preferences -> Add-ons -> Install
* Find and select downloaded ZIP file
* Press Install Add-on button
* Enable add-on's checkbox

# LOCATION:
Render Properties -> Collection Visibility Controls

# USE:
* Activate checkbox enables/disables add-on for the current scene
* To add visibility control Empty objects to each collection in the current scene press Controllers Setup button
* While Activate checkbox is enabled, on each frame change collection visibility (Render, Viewport and Select) will be changed to its controller's visibility 
* You can keyframe controllers visibility to change collections visibility during the scene's frame range
* You can choose what type of visibility (Render, Viewport, Select) will be affected by add-on with the buttons below the Controllers Setup button
