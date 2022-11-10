"""

raylibExtras * Utilities and Shared Components for raypyc

FreeCamC * Free flight sim style camera (Python version)

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
import math

import raypyc


class FreeCamera(ctypes.Structure):
    _fields_ = [
        ('Position', raypyc.Vector3),  # Camera position
        ('Forward', raypyc.Vector3),  # Camera target it looks-at
        ('Up', raypyc.Vector3),  # Camera up vector (rotation over its axis)
    ]

    @property
    def Position(self) -> raypyc.Vector3:
        return self.Position

    @Position.setter
    def Position(self, i: raypyc.Vector3) -> None:
        self.Position = i

    @property
    def Forward(self) -> raypyc.Vector3:
        return self.Forward

    @Forward.setter
    def Forward(self, i: raypyc.Vector3) -> None:
        self.Forward = i

    @property
    def Up(self) -> raypyc.Vector3:
        return self.Up

    @Up.setter
    def Up(self, i: raypyc.Vector3) -> None:
        self.Up = i


def free_camera_init(camera: ctypes.POINTER(FreeCamera), position: raypyc.Vector3, up: raypyc.Vector3) -> None:
    """called to initialize a camera to default values"""
    camera.contents.Position = position
    camera.contents.Up = up
    if math.fabs(camera.contents.Up.z) > 0.1:
        camera.contents.Forward = raypyc.Vector2(0, 1, 0)
    else:
        camera.contents.Forward = raypyc.Vector2(0, 0, 1)


def free_camera_to_camera(camera: ctypes.POINTER(FreeCamera), raylib_camera: ctypes.POINTER(raypyc.Camera3D)) -> None:
    """called to fill out a raylib camera"""
    raylib_camera.contents.position = camera.contents.Position
    raylib_camera.contents.target = raypyc.vector3_add(camera.contents.Position, camera.contents.Forward)
    raylib_camera.contents.up = camera.contents.Up


def free_camera_look_at(camera: ctypes.POINTER(FreeCamera), target: raypyc.Vector3, up: raypyc.Vector3) -> None:
    """called to set the target the camera should look at"""
    camera.contents.Forward = raypyc.vector3_normalize(raypyc.vector3_subtract(target, camera.contents.Position))
    camera.contents.Up = raypyc.vector3_normalize(up)


def free_camera_set_position(camera: ctypes.POINTER(FreeCamera), position: raypyc.Vector3) -> None:
    """called to set where the camera is"""
    camera.contents.Position = position


# Called to move the camera relative to it's current orientation
def free_camera_move_forward(camera: ctypes.POINTER(FreeCamera), distance: ctypes.c_float) -> None:
    camera.contents.Position = raypyc.vector3_add(camera.contents.Position, raypyc.vector3_scale(camera.contents.Forward, distance))


def free_camera_move_up(camera: ctypes.POINTER(FreeCamera), distance: ctypes.c_float) -> None:
    camera.contents.Position = raypyc.vector3_add(camera.contents.Position, raypyc.vector3_scale(camera.contents.Up, distance))


def get_right_vector(camera: ctypes.POINTER(FreeCamera)) -> raypyc.Vector3:
    return raypyc.vector3_cross_product(camera.contents.Forward, camera.contents.Up)


# Called to rotate the camera relative to it's current orientation
def free_camera_rotate_yaw(camera: ctypes.POINTER(FreeCamera), angle: ctypes.c_float) -> None:
    matrix: raypyc.Matrix = raypyc.matrix_rotate(camera.contents.Up, raypyc.DEG2RAD * angle)
    camera.contents.Forward = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Forward, matrix))


def free_camera_rotate_pitch(camera: ctypes.POINTER(FreeCamera), angle: ctypes.c_float) -> None:
    angle = math.fmod(angle, 360)
    if angle < 0:
        angle += 360

    matrix: raypyc.Matrix = raypyc.matrix_rotate(get_right_vector(camera), DEG2RAD * -angle)

    camera.contents.Up = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Up, matrix))
    camera.contents.Forward = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Forward, matrix))


def free_camera_rotate_roll(camera: ctypes.POINTER(FreeCamera), angle: ctypes.c_float) -> None:
    matrix: raypyc.Matrix = raypyc.matrix_rotate(camera.contents.Forward, raypyc.DEG2RAD * angle)
    camera.contents.Up = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Up, matrix))


# called to rotate the camera around a world axis (Y or Z)
def free_camera_rotate_heading(camera: ctypes.POINTER(FreeCamera), angle: ctypes.c_float, use_y: ctypes.c_bool) -> None:
    matrix: raypyc.Matrix = raypyc.Matrix()

    if use_y:
        matrix = raypyc.matrix_rotate_y(raypyc.DEG2RAD * angle)
    else:
        matrix = raypyc.matrix_rotate_z(raypyc.DEG2RAD * angle)

    camera.contents.Up = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Up, matrix))
    camera.contents.Forward = raypyc.vector3_normalize(raypyc.vector3_transform(camera.contents.Forward, matrix))
