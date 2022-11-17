# rlFPCamera
A simple first person camera controller for raylib(with raypyc)

# API
All data for the first person camera is managed by the rlFPCamera class.

This structure is set up by calling rlFPCamera_init with a camera(pointer), FOV, and Position.
```
rlFPCamera_init(pointer(camera), fov, pos)
```

The fov argument is the vertical field of view, 45 degrees is a good starting point. The horizontal view will be computed using the aspect ratio of the screen.
The position will be the initial location of the camera in world space.

Once the camera is initialized, options in the camera structure can be set, such as view bob, speed, control keys, and render distance.

Whenever a window, or render texture is resized rlFPCamera_resize_view needs to be called for any cameras used in that space, to properly recompute the FOV.

Once per frame rlFPCamera_update with the camera should be called, this will apply any input events and move the camera.
Once a camera is updated it can be used on screen or in a render texture by calling.

rlFPCamera_begin_mode_3d and rlFPCamera_end_mode_3d. These work just like begin_mode_3d and end_mode_3d for raylib cameras, but use the extended features of rlFPCamera

