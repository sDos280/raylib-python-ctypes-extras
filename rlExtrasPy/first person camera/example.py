"""

raylib [core] example - First Person Orbit Camera Example

"""

# Import
# ------------------------------------------------------------------------------------
from raypyc import *

from first_person_camera import *


# ------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------
# Program main entry point
# ------------------------------------------------------------------------------------
def main():
    # Initialization
    # ------------------------------------------------------------------------------------
    SCREEN_WIDTH = 1900
    SCREEN_HEIGHT = 900

    set_config_flags(ConfigFlags.FLAG_MSAA_4X_HINT | ConfigFlags.FLAG_VSYNC_HINT)
    init_window(SCREEN_WIDTH, SCREEN_HEIGHT, b"raylib-extras [camera] example - First person camera")
    # ------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------
    img = gen_image_checked(256, 256, 32, 32, DARKGRAY, WHITE)
    tx = load_texture_from_image(img)
    unload_image(img)
    set_texture_filter(tx, TextureFilter.TEXTURE_FILTER_ANISOTROPIC_16X)
    set_texture_wrap(tx, TextureWrap.TEXTURE_WRAP_CLAMP)

    # setup initial camera data
    cam = FirstPersonCamera()
    rl_first_person_camera_init(ctypes.pointer(cam), 45, Vector3(1, 0, 0))
    cam.MoveSpeed.z = 10
    cam.MoveSpeed.x = 5

    cam.FarPlane = 5000

    # Main game loop
    while not window_should_close():  # Detect window close button or ESC key
        # Update
        # ----------------------------------------------------------------------------------
        if is_key_pressed(KeyboardKey.KEY_F1):
            cam.AllowFlight = not cam.AllowFlight

        rl_first_person_camera_update(ctypes.pointer(cam))
        # ----------------------------------------------------------------------------------

        # Draw
        # ----------------------------------------------------------------------------------
        begin_drawing()
        clear_background(RAYWHITE)

        rl_first_person_camera_begin_mode_3d(ctypes.pointer(cam))

        # grid of cube trees on a plane to make a "world"
        draw_plane(Vector3(0, 0, 0), Vector2(50, 50), BEIGE)  # simple world plane
        spacing = 4.0
        count = 5

        total = 0
        vis = 0

        for x in range(int(-count * spacing), int(count * spacing), int(spacing)):
            for z in range(int(-count * spacing), int(count * spacing), int(spacing)):
                pos = Vector3(x, 0.5, z)

                minv = Vector3(x - 0.5, 0, z - 0.5)
                maxv = Vector3(x + 0.5, 1, z + 0.5)

                draw_cube_texture(tx, pos, 1, 1, 1, GREEN)
                draw_cube_texture(tx, pos, 0.25, 1, 0.25, BROWN)

        rl_first_person_camera_end_mode_3d()
        draw_text(f"Forward: <{cam.Forward.x}, {cam.Forward.y}, {cam.Forward.z}>".encode(), 50, 50, 20, BLACK)
        draw_text(f"<Pos: {cam.CameraPosition.x}, {cam.CameraPosition.y}, {cam.CameraPosition.z}>".encode(), 50, 80, 20, BLACK)

        if cam.AllowFlight:
            draw_text(b"(F1) Flight", 2, 20, 20, BLACK)
        else:
            draw_text(b"(F1) Running", 2, 20, 20, BLACK)

        # instructions
        draw_fps(0, 0)
        end_drawing()
        # ----------------------------------------------------------------------------------

    # De-Initialization
    # ----------------------------------------------------------------------------------
    close_window()  # Close window and OpenGL context
    # ----------------------------------------------------------------------------------


# Execute the main function
if __name__ == '__main__':
    main()