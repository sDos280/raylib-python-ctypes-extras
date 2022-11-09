"""

# raylibExtras * Utilities and Shared Components for raypyc

"""

import ctypes
import enum

import raypyc


class CameraControls(enum.IntEnum):
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
        ('ControlsKeys', ctypes.c_int * CameraControls.LAST_CONTROL),

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

        # state for mouse movement
        ('PreviousMousePosition', raypyc.Vector2),

        # state for view movement
        ('TargetDistance', ctypes.c_float),

        # state for view angles
        ('ViewAngles', raypyc.Vector2),

        # state for bobble
        ('CurrentBobble', ctypes.c_float),

        # state for window focus
        ('Focused', ctypes.c_bool),

        # raylib camera for use with raylib modes
        ('ViewCamera', raypyc.Camera3D),

        ('Forward', raypyc.Vector3),
        ('Right', raypyc.Vector3),

        # clipping planes
        # note must use begin_mode_fp_3d and end_mode_fp_3d instead of begin_mode_3d/end_mode_3d for clipping planes to work
        ('NearPlane', ctypes.c_double),
        ('FarPlane', ctypes.c_double)
    ]


def init_first_person_camera(camera: ctypes.POINTER(FirstPersonCamera), fov_y: ctypes.c_float, position: raypyc.Vector3) -> None:
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

    camera.contents.PreviousMousePosition = raypyc.get_mouse_position()
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
    camera.contents.ViewCamera.fov_y = fov_y
    camera.contents.ViewCamera.projection = raypyc.CameraProjection.CAMERA_PERSPECTIVE

    camera.contents.NearPlane = 0.01
    camera.contents.FarPlane = 1000.0

    """resize_firstPersonCamera_view(camera)
    use_firstPersonCamera_mouse(camera, camera.contents.UseMouse)"""
