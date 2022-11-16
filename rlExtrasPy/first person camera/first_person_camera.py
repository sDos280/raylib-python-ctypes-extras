"""

raylibExtras * Utilities and Shared Components for raypyc

FPCamera * Simple First person camera (C version)

LICENSE: MIT

Copyright (c) 2020 Jeffery Myers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import ctypes
import enum
import math

import raypyc

RL_CULL_DISTANCE_NEAR: float = 0.01  # Default projection matrix near cull distance  (currently raypyc don't wrap config.h)


class rlFirstPersonCameraControls(enum.IntEnum):
    MOVE_FRONT = 0
    MOVE_BACK = enum.auto()
    MOVE_RIGHT = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    TURN_LEFT = enum.auto()
    TURN_RIGHT = enum.auto()
    TURN_UP = enum.auto()
    TURN_DOWN = enum.auto()
    SPRINT = enum.auto()
    LAST_CONTROL = enum.auto()


class FirstPersonCamera(ctypes.Structure):
    _fields_ = [
        # keys used to control the camera
        ('ControlsKeys', ctypes.c_int * rlFirstPersonCameraControls.LAST_CONTROL),

        # the speed in units/second to move
        # X = sidestep
        # Y = jump/fall
        # Z = forward
        ('MoveSpeed', raypyc.Vector3),

        # the speed for turning when using keys to look
        # degrees/second
        ('TurnSpeed', raypyc.Vector2),

        # use the mouse for looking?
        ('UseMouse', ctypes.c_bool),

        # how many pixels equate out to an angle move, larger numbers mean slower, more accurate mouse
        ('MouseSensitivity', ctypes.c_float),

        # how far down can the camera look
        ('MinimumViewY', ctypes.c_float),

        # how far up can the camera look
        ('MaximumViewY', ctypes.c_float),

        # how fast the view should bobble as you move
        # defaults to 0 for no bobble
        ('ViewBobbleFreq', ctypes.c_float),

        # how high up/down will the bobble be
        ('ViewBobbleMagnitude', ctypes.c_float),

        # how far left and right should the view bobble
        ('ViewBobbleWaverMagnitude', ctypes.c_float),

        # the position of the base of the camera (on the floor)
        # note that this will not be the view position because it is offset by the eye height.
        # this value is also not changed by the view bobble
        ('CameraPosition', raypyc.Vector3),

        # how far from the base of the camera is the player's view
        ('PlayerEyesPosition', ctypes.c_float),

        # the field of view in X and Y
        ('FOV', raypyc.Vector2),

        # state for view movement
        ('TargetDistance', ctypes.c_float),

        # state for view angles
        ('ViewAngles', raypyc.Vector2),

        # state for bobble
        ('CurrentBobble', ctypes.c_float),

        # state for window focus
        ('Focused', ctypes.c_bool),

        ('AllowFlight', ctypes.c_bool),

        # raylib camera for use with raylib modes
        ('ViewCamera', raypyc.Camera3D),

        ('Forward', raypyc.Vector3),
        ('Right', raypyc.Vector3),

        # clipping planes
        # note must use begin_mode_fp_3d and end_mode_fp_3d instead of begin_mode_3d/end_mode_3d for clipping planes to work
        ('NearPlane', ctypes.c_double),
        ('FarPlane', ctypes.c_double)
    ]


def rl_first_person_camera_init(camera: ctypes.POINTER(FirstPersonCamera), fov_y: ctypes.c_float, position: raypyc.Vector3) -> None:
    """called to initialize a camera to default values"""
    if not bool(camera):  # NULL pointers have a False boolean value
        return

    camera.contents.ControlsKeys[0] = ord('W')
    camera.contents.ControlsKeys[1] = ord('S')
    camera.contents.ControlsKeys[2] = ord('D')
    camera.contents.ControlsKeys[3] = ord('A')
    camera.contents.ControlsKeys[4] = ord('E')
    camera.contents.ControlsKeys[5] = ord('Q')
    camera.contents.ControlsKeys[6] = raypyc.KeyboardKey.KEY_LEFT
    camera.contents.ControlsKeys[7] = raypyc.KeyboardKey.KEY_RIGHT
    camera.contents.ControlsKeys[8] = raypyc.KeyboardKey.KEY_UP
    camera.contents.ControlsKeys[9] = raypyc.KeyboardKey.KEY_DOWN
    camera.contents.ControlsKeys[10] = raypyc.KeyboardKey.KEY_LEFT_SHIFT

    camera.contents.MoveSpeed = raypyc.Vector3(1, 1, 1)
    camera.contents.TurnSpeed = raypyc.Vector2(90, 90)

    camera.contents.UseMouse = True
    camera.contents.MouseSensitivity = 600

    camera.contents.MinimumViewY = -89.0
    camera.contents.MaximumViewY = 89.0

    camera.contents.ViewBobbleFreq = 0.0
    camera.contents.ViewBobbleMagnitude = 0.02
    camera.contents.ViewBobbleWaverMagnitude = 0.002
    camera.contents.CurrentBobble = 0

    camera.contents.Focused = raypyc.is_window_focused()

    camera.contents.TargetDistance = 1
    camera.contents.PlayerEyesPosition = 0.5
    camera.contents.ViewAngles = raypyc.Vector2(0, 0)

    camera.contents.CameraPosition = position
    camera.contents.FOV.y = fov_y

    camera.contents.ViewCamera.position = position
    camera.contents.ViewCamera.position.y += camera.contents.PlayerEyesPosition
    camera.contents.ViewCamera.target = raypyc.vector3_add(camera.contents.ViewCamera.position, raypyc.Vector3(0, 0, camera.contents.TargetDistance))
    camera.contents.ViewCamera.up = raypyc.Vector3(0.0, 1.0, 0.0)
    camera.contents.ViewCamera.fovy = fov_y
    camera.contents.ViewCamera.projection = raypyc.CameraProjection.CAMERA_PERSPECTIVE

    camera.contents.AllowFlight = False

    camera.contents.NearPlane = 0.01
    camera.contents.FarPlane = 1000.0

    rl_first_person_camera_resize_view(camera)
    rl_first_person_camera_use_mouse(camera, camera.contents.UseMouse)


def rl_first_person_camera_use_mouse(camera: ctypes.POINTER(FirstPersonCamera), use_mouse: ctypes.c_bool) -> None:
    """turn the use of mouse-look on/off, also updates the cursor visibility"""
    if not bool(camera):  # NULL pointers have a False boolean value
        return

    camera.contents.UseMouse = use_mouse

    if use_mouse and raypyc.is_window_focused():
        raypyc.disable_cursor()
    elif (not use_mouse) and raypyc.is_window_focused():
        raypyc.enable_cursor()


def rl_first_person_camera_resize_view(camera: ctypes.POINTER(FirstPersonCamera)) -> None:
    """called to update field of view in X when window resizes"""

    if not bool(camera):  # NULL pointers have a False boolean value
        return

    width: float = float(raypyc.get_screen_width())
    height: float = float(raypyc.get_screen_height())

    camera.contents.FOV.y = camera.contents.ViewCamera.fovy

    if height != 0:
        camera.contents.FOV.x = camera.contents.FOV.y * (width / height)


def rl_first_person_camera_get_position(camera: ctypes.POINTER(FirstPersonCamera)) -> raypyc.Vector3:
    """Get the camera's position in world (or game) space"""
    return camera.contents.CameraPosition


def rl_first_person_camera_set_position(camera: ctypes.POINTER(FirstPersonCamera), pos: raypyc.Vector3) -> None:
    """Get the camera's position in world (or game) space"""
    camera.contents.CameraPosition = pos
    forward: raypyc.Vector3 = raypyc.vector3_subtract(camera.contents.ViewCamera.target, camera.contents.ViewCamera.position)
    camera.contents.ViewCamera.position = camera.contents.CameraPosition
    camera.contents.ViewCamera.target = raypyc.vector3_add(camera.contents.CameraPosition, forward)


def rl_first_person_camera_get_view_ray(camera: ctypes.POINTER(FirstPersonCamera)) -> raypyc.Ray:
    """returns the ray from the camera through the center of the view"""
    return raypyc.Ray(camera.ViewCamera.CameraPosition, camera.ViewCamera.Forward)


def _get_speed_for_axis(camera: ctypes.POINTER(FirstPersonCamera), axis: rlFirstPersonCameraControls, speed: ctypes.c_float) -> ctypes.c_float:
    if not bool(camera):  # NULL pointers have a False boolean value
        return

    key: int = camera.contents.ControlsKeys[axis]
    if key == -1:
        return 0

    factor = 1.0
    if raypyc.is_key_down(camera.contents.ControlsKeys[rlFirstPersonCameraControls.SPRINT]):
        factor = 2

    if raypyc.is_key_down(camera.contents.ControlsKeys[axis]):
        return speed * raypyc.get_frame_time() * factor

    return 0.0


def rl_first_person_camera_update(camera: ctypes.POINTER(FirstPersonCamera)) -> None:
    """update the camera for the current frame"""
    if not bool(camera):  # NULL pointers have a False boolean value
        return

    if (raypyc.is_window_focused() != camera.contents.Focused) and camera.contents.UseMouse:
        camera.contents.Focused = raypyc.is_window_focused()
        if camera.contents.Focused:
            raypyc.disable_cursor()
        else:
            raypyc.enable_cursor()

    # Mouse movement detection
    mouse_position_delta: raypyc.Vector2 = raypyc.get_mouse_delta()

    # Keys input detection
    direction: ctypes.Array[ctypes.c_float] = (ctypes.c_float * (rlFirstPersonCameraControls.MOVE_DOWN + 1))(
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_FRONT, camera.contents.MoveSpeed.z),
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_BACK, camera.contents.MoveSpeed.z),
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_RIGHT, camera.contents.MoveSpeed.x),
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_LEFT, camera.contents.MoveSpeed.x),
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_UP, camera.contents.MoveSpeed.y),
        _get_speed_for_axis(camera, rlFirstPersonCameraControls.MOVE_DOWN, camera.contents.MoveSpeed.y)
    )

    # let someone modify the projected position
    # Camera orientation calculation
    turn_rotation: float = _get_speed_for_axis(camera, rlFirstPersonCameraControls.TURN_RIGHT, camera.contents.TurnSpeed.x) - _get_speed_for_axis(camera, rlFirstPersonCameraControls.TURN_LEFT, camera.contents.TurnSpeed.x)
    tilt_rotation: float = _get_speed_for_axis(camera, rlFirstPersonCameraControls.TURN_UP, camera.contents.TurnSpeed.y) - _get_speed_for_axis(camera, rlFirstPersonCameraControls.TURN_DOWN, camera.contents.TurnSpeed.y)

    if turn_rotation != 0:
        camera.contents.ViewAngles.x -= turn_rotation * raypyc.DEG2RAD
    elif camera.contents.UseMouse and camera.contents.Focused:
        camera.contents.ViewAngles.x += (mouse_position_delta.x / camera.contents.MouseSensitivity)

    if tilt_rotation:
        camera.contents.ViewAngles.y += tilt_rotation * raypyc.DEG2RAD
    elif camera.contents.UseMouse and camera.contents.Focused:
        camera.contents.ViewAngles.y += (mouse_position_delta.y / camera.contents.MouseSensitivity)

    # Angle clamp
    if camera.contents.ViewAngles.y < camera.contents.MinimumViewY * raypyc.DEG2RAD:
        camera.contents.ViewAngles.y = camera.contents.MinimumViewY * raypyc.DEG2RAD
    elif camera.contents.ViewAngles.y > camera.contents.MaximumViewY * raypyc.DEG2RAD:
        camera.contents.ViewAngles.y = camera.contents.MaximumViewY * raypyc.DEG2RAD

    # Recalculate camera target considering translation and rotation
    target: raypyc.Vector3 = raypyc.vector3_transform(raypyc.Vector3(0, 0, 1), raypyc.matrix_rotate_zyx(raypyc.Vector3(camera.contents.ViewAngles.y, -camera.contents.ViewAngles.x, 0)))

    if camera.contents.AllowFlight:
        camera.contents.Forward = target
    else:
        camera.contents.Forward = raypyc.vector3_transform(raypyc.Vector3(0, 0, 1), raypyc.matrix_rotate_zyx(raypyc.Vector3(0, -camera.contents.ViewAngles.x, 0)))

    camera.contents.Right = raypyc.Vector3(camera.contents.Forward.z * -1.0, 0, camera.contents.Forward.x)

    camera.contents.CameraPosition = raypyc.vector3_add(camera.contents.CameraPosition, raypyc.vector3_scale(camera.contents.Forward, direction[rlFirstPersonCameraControls.MOVE_FRONT] - direction[rlFirstPersonCameraControls.MOVE_BACK]))
    camera.contents.CameraPosition = raypyc.vector3_add(camera.contents.CameraPosition, raypyc.vector3_scale(camera.contents.Right, direction[rlFirstPersonCameraControls.MOVE_RIGHT] - direction[rlFirstPersonCameraControls.MOVE_LEFT]))

    camera.contents.CameraPosition.y += direction[rlFirstPersonCameraControls.MOVE_UP] - direction[rlFirstPersonCameraControls.MOVE_DOWN]

    camera.contents.ViewCamera.position = camera.contents.CameraPosition

    eye_offset: float = camera.contents.PlayerEyesPosition

    if camera.contents.ViewBobbleFreq > 0:
        swing_delta: float = float(max(math.fabs(direction[rlFirstPersonCameraControls.MOVE_FRONT] - direction[rlFirstPersonCameraControls.MOVE_BACK]),
                                       math.fabs(direction[rlFirstPersonCameraControls.MOVE_RIGHT] - direction[rlFirstPersonCameraControls.MOVE_LEFT])))

        camera.contents.CurrentBobble += swing_delta * camera.contents.ViewBobbleFreq

        viewBobbleDampen: float = 8.0

        eye_offset -= math.sin(camera.contents.CurrentBobble / viewBobbleDampen) * camera.contents.ViewBobbleMagnitude

        camera.contents.ViewCamera.up.x = math.sin(camera.contents.CurrentBobble / (viewBobbleDampen * 2)) * camera.contents.ViewBobbleWaverMagnitude
        camera.contents.ViewCamera.up.z = -math.sin(camera.contents.CurrentBobble / (viewBobbleDampen * 2)) * camera.contents.ViewBobbleWaverMagnitude

    else:
        camera.contents.CurrentBobble = 0
        camera.contents.ViewCamera.up.x = 0
        camera.contents.ViewCamera.up.z = 0

    camera.contents.ViewCamera.position.y += eye_offset

    camera.contents.ViewCamera.target.x = camera.contents.ViewCamera.position.x + target.x
    camera.contents.ViewCamera.target.y = camera.contents.ViewCamera.position.y + target.y
    camera.contents.ViewCamera.target.z = camera.contents.ViewCamera.position.z + target.z


def _setup_camera(camera: ctypes.POINTER(FirstPersonCamera), aspect: ctypes.c_float) -> None:
    raypyc.rl_draw_render_batch_active()  # Draw Buffers (Only OpenGL 3+ and ES2)
    raypyc.rl_matrix_mode(raypyc.RL_PROJECTION)  # Switch to projection matrix
    raypyc.rl_push_matrix()  # Save previous matrix, which contains the settings for the 2d ortho projection
    raypyc.rl_load_identity()  # Reset current matrix (projection)

    if camera.contents.ViewCamera.projection == raypyc.CameraProjection.CAMERA_PERSPECTIVE:
        # Setup perspective projection
        top: float = RL_CULL_DISTANCE_NEAR * math.tan(camera.contents.ViewCamera.fovy * 0.5 * raypyc.DEG2RAD)
        right: float = top * aspect

        raypyc.rl_frustum(-right, right, -top, top, camera.contents.NearPlane, camera.contents.FarPlane)

    elif camera.contents.ViewCamera.projection == raypyc.CameraProjection.CAMERA_ORTHOGRAPHIC:
        # Setup orthographic projection
        top: float = camera.contents.ViewCamera.fovy / 2.0
        right: float = top * aspect

        raypyc.rl_ortho(-right, right, -top, top, camera.contents.NearPlane, camera.contents.FarPlane)

    # NOTE: zNear and zFar values are important when computing depth buffer values

    raypyc.rl_matrix_mode(raypyc.RL_MODELVIEW)  # Switch back to model-view matrix
    raypyc.rl_load_identity()  # Reset current matrix (model-view)

    # Setup Camera view
    mat_view: raypyc.Matrix = raypyc.matrix_look_at(camera.contents.ViewCamera.position, camera.contents.ViewCamera.target, camera.contents.ViewCamera.up)

    raypyc.rl_mult_matrixf(raypyc.matrix_to_float_v(mat_view).v)  # Multiply model-view matrix by view matrix (camera)

    raypyc.rl_enable_depth_test()  # Enable DEPTH_TEST for 3D


def rl_first_person_camera_begin_mode_3d(camera: ctypes.POINTER(FirstPersonCamera)) -> None:
    """start drawing using the camera, with near/far plane support"""
    if not bool(camera):  # NULL pointers have a False boolean value
        return

    aspect: float = float(raypyc.get_screen_width()) / float(raypyc.get_screen_height())
    _setup_camera(camera, aspect)


def rl_first_person_camera_end_mode_3d() -> None:
    """end drawing with the camera"""
    raypyc.end_mode_3d()
