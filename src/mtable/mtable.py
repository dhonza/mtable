import numpy as np
import time

from gpiozero import LineSensor, Motor

class MeasurementTable(object):
    def __init__(self, 
                 motor_forward_pin=24, 
                 motor_backward_pin=23, 
                 motor_enable_pin=25,
                 motor_speed=1.0,
                 lsensor_pin=16, 
                 lsensor_sample_rate=300,
                 lsensor_resolution_deg=1.0
                ):
        self.motor = Motor(forward=motor_forward_pin, backward=motor_backward_pin, enable=motor_enable_pin)
        self.motor_speed = motor_speed
        self.lsensor = LineSensor(lsensor_pin, sample_rate=lsensor_sample_rate)
        self.lsensor_resolution_deg = lsensor_resolution_deg
        self.reset()
        
        def inc():
            self.times.append(time.time())
            if self.fwddir:
                self.cnt += 1
            elif self.bckdir:
                self.cnt -= 1
            if self.cnt == self.target:
                self.targetf()                
        
        self.lsensor.when_line = inc
        self.lsensor.when_no_line = inc

        
    def _normalizeangle(self, a):
        a %= 360.0
        if a < 0:
            a += 360
        return a
        
    def angle(self):
        # angle <0;360) in degrees (zero for cnt = 0)
        a = self.cnt * self.lsensor_resolution_deg
        return self._normalizeangle(a)
        
    def state(self):
        return {'cnt': self.cnt, 
                'angle': self.angle(), 
                'speed': self.motor_speed,
                'fwddir': self.fwddir,
                'bckdir': self.bckdir,
                'active': self.motor.is_active}
    
    def close(self):
        self.lsensor.close()
        self.reset()
        
    def reset(self):
        self.cnt = 0
        self.fwddir = False
        self.bckdir = False
        self.target = -1
        self.times = []
        
    def set_speed(self, speed):
        assert 0.0 < speed <= 1.0
        self.motor_speed = speed
    
    def waitfor(self, target, targetf):
        self.target = target
        self.targetf = targetf
        
    def rotate_async(self, deg):
        if self.motor.is_active:
            return False
        
        nsteps = round(deg / (self.lsensor_resolution_deg))   
            
        self.waitfor(self.cnt + nsteps, self.stop)
        if nsteps > 0:
            self.fwddir = True
            self.bckdir = False
            self.motor.forward(self.motor_speed)
        elif nsteps < 0:
            self.fwddir = False
            self.bckdir = True
            self.motor.backward(self.motor_speed)
            
    def rotateto_async(self, angle):
        angle = self._normalizeangle(angle)
        current = self.angle()
        print(f"angle: {angle}, current: {current}")
        diff_fwd = angle-current if angle >= current else angle + 360 - current
        diff_bck = current-angle if angle <= current else current + 360 - angle
        print(f"diff_fwd: {diff_fwd}, diff_bck: {diff_bck}")
        if diff_fwd < diff_bck:
            self.rotate_async(diff_fwd)
        else:
            self.rotate_async(-diff_bck)            
            
    def wait_for_stop(self):
        # this can be done much better, I guess
        while self.motor.is_active:
            time.sleep(0.1)        
      
    def rotate(self, deg):
        self.rotate_async(deg)
        self.wait_for_stop()

    def rotateto(self, angle):
        self.rotateto_async(angle)
        self.wait_for_stop()
            
    def stop(self):
        self.motor.stop()
        self.fwddir = False
        self.bckdir = False
        
        