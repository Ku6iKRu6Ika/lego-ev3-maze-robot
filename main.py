#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


SPEED = 1000                  # Скорость
ANGLE_FORWARD = 612           # Сколько градсов вперед
ANGLE_TURN = 250              # Сколько градсов поворот
ANGLE_ALIGN = 190             # Сколько градусов выравнивание
MM_LET = 15 * 10              # Расстояние до стены в мм
FINISH_COLOR = Color.GREEN    # Цвет финиша

COLOR_SENSOR = ColorSensor(Port.S3)               # Датчик цвета, 3 порт
ULTRASONIC_SENSOR_F = UltrasonicSensor(Port.S4)   # Ультразвуковой датчик спереди, 4 порт
ULTRASONIC_SENSOR_R = UltrasonicSensor(Port.S1)   # Ультразвуковой датчик справа, 1 порт
MOTOR_L = Motor(Port.B)                           # Левый мотор, порт B
MOTOR_R = Motor(Port.C)                           # Правый мотор, порт C

FORWARD = 0
RIGHT = 1
LEFT = -1


# Движение вперед
def forward():
    MOTOR_L.run_angle(SPEED, ANGLE_FORWARD, wait=False)
    MOTOR_R.run_angle(SPEED, ANGLE_FORWARD)
    
    
# Сделать выравнивание вперед
def align_forward():
    MOTOR_L.run_angle(SPEED, ANGLE_ALIGN, wait=False)
    MOTOR_R.run_angle(SPEED, ANGLE_ALIGN)
    
    MOTOR_L.run_angle(-SPEED, ANGLE_ALIGN, wait=False)
    MOTOR_R.run_angle(-SPEED, ANGLE_ALIGN)
    

# Сделать выравнивание назад
def align_back():
    MOTOR_L.run_angle(-SPEED, ANGLE_ALIGN, wait=False)
    MOTOR_R.run_angle(-SPEED, ANGLE_ALIGN)
    
    MOTOR_L.run_angle(SPEED, ANGLE_ALIGN, wait=False)
    MOTOR_R.run_angle(SPEED, ANGLE_ALIGN)


# Сделать поворот
def turn(direction):
    if direction == 'right':
        MOTOR_L.run_angle(SPEED, ANGLE_TURN, wait=False)
        MOTOR_R.run_angle(-SPEED, ANGLE_TURN)
    elif direction == 'left':
        MOTOR_L.run_angle(-SPEED, ANGLE_TURN, wait=False)
        MOTOR_R.run_angle(SPEED, ANGLE_TURN)


# Прохождение лабиринта по правилу правой руки
def finding_way():
    way = []
    
    while COLOR_SENSOR.color() != FINISH_COLOR:
        if ULTRASONIC_SENSOR_R.distance() > MM_LET:
            align_forward()
            turn('right')
            align_back()
            forward()
            
            way.append(RIGHT)
            way.append(FORWARD)
        else:
            if ULTRASONIC_SENSOR_F.distance() > MM_LET:
                forward()
                way.append(FORWARD)
            else:
                align_forward()
                turn('left')
                align_back()
                way.append(LEFT)
                
                if ULTRASONIC_SENSOR_F.distance() > MM_LET:
                    forward()
                    way.append(FORWARD)
                    
    return way
                    
                    
# Прохождение лабиринта по заданному пути
def passing_way(way):
    for action in way:
        if action == FORWARD:
            forward()
        elif action == LEFT:
            align_forward()
            turn('left')
            align_back()
        elif action == RIGHT:
            align_forward()
            turn('right')
            align_back()
  
                    
# Обработка пути: удаление тупиков, сделать обратным                    
def process_way(way):
    index = 0
    
    while index < len(way):
        if way[index] == LEFT and way[index-1] == LEFT:
            way.pop(index)
            way.pop(index-1)
            index -= 2
            
            while (
                (way[index] == FORWARD and way[index+1] == FORWARD) or
                (way[index] == RIGHT and way[index+1] == LEFT) or
                (way[index] == LEFT and way[index+1] == RIGHT)
            ):
                way.pop(index)
                way.pop(index)
                index -= 1
                
                
            if way[index] == FORWARD:
                way[index+1] *= -1
            else:
                way[index] *= -1
                
        if (way[index] == LEFT and way[index+1] == RIGHT) or (way[index] == RIGHT and way[index+1] == LEFT):
            way.pop(index)
            way.pop(index)
            index -= 1
            
        index += 1
    
    return [-1, -1] + list(map(lambda x: x * -1, way[::-1]))


def main():
    ev3 = EV3Brick()
    
    ev3.screen.print('Finding a way...')
    way = finding_way()
    way = process_way(way)
    
    ev3.screen.print('Wait 1 seconds...')
    wait(1000)
    
    ev3.screen.print('Passing...')
    passing_way(way)


main()
