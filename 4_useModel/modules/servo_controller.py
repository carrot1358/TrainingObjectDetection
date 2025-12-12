#!/usr/bin/env python3
"""
servo_controller.py
MG90S Servo Controller for Raspberry Pi
Provides simple methods for controlling servo position
"""

from time import sleep
import sys

class ServoController:
    """
    Servo controller for MG90S on Raspberry Pi using gpiozero.
    Provides intuitive methods for servo control with safety features.

    Example:
        servo = ServoController(gpio_pin=18, home_angle=90)
        servo.move(45)        # Move to 45 degrees
        servo.move_left(30)   # Move 30 degrees left from current
        servo.home()          # Return to 90 degrees
        servo.cleanup()       # Release GPIO resources
    """

    def __init__(self, gpio_pin=18, min_angle=0, max_angle=180,
                 home_angle=90, min_pulse_width=0.5/1000,
                 max_pulse_width=2.5/1000, frame_width=20/1000,
                 angle_offset=0, debug=False):
        """
        Initialize servo on specified GPIO pin.

        Args:
            gpio_pin (int): BCM GPIO pin number (default: 18)
            min_angle (int): Minimum servo angle in degrees (default: 0)
            max_angle (int): Maximum servo angle in degrees (default: 180)
            home_angle (int): Home/center position in degrees (default: 90)
            min_pulse_width (float): Minimum pulse width in seconds (default: 0.5ms)
            max_pulse_width (float): Maximum pulse width in seconds (default: 2.5ms)
            frame_width (float): PWM frame period in seconds (default: 20ms = 50Hz)
            angle_offset (int): Calibration offset in degrees (default: 0)
                               Positive = shift right, Negative = shift left
            debug (bool): Enable debug logging (default: False)
        """
        self.gpio_pin = gpio_pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.home_angle = home_angle
        self.frame_width = frame_width
        self.angle_offset = angle_offset
        self.debug = debug
        self.current_angle = home_angle
        self.servo = None

        # Initialize servo using gpiozero (lgpio pin factory must be set before importing this module)
        from gpiozero import AngularServo

        self.servo = AngularServo(
            gpio_pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
            frame_width=frame_width
        )

        if self.debug:
            print(f"[ServoController] Initialized on GPIO {gpio_pin}")

        # Move to home position
        self.home()

    def _clamp_angle(self, angle):
        """
        Clamp angle to valid range to prevent mechanical damage.

        Args:
            angle (float): Desired angle

        Returns:
            float: Clamped angle within min_angle and max_angle
        """
        return max(self.min_angle, min(self.max_angle, angle))

    def move(self, angle):
        """
        Move servo to absolute angle position with calibration applied.

        Args:
            angle (float): Target angle in degrees (0-180)
        """
        angle = self._clamp_angle(angle)

        # Apply calibration offset
        calibrated_angle = angle + self.angle_offset
        calibrated_angle = self._clamp_angle(calibrated_angle)

        self.servo.angle = calibrated_angle
        self.current_angle = angle  # Store requested angle, not calibrated

        if self.debug:
            if self.angle_offset != 0:
                print(f"[ServoController] Moved to {angle}° (calibrated: {calibrated_angle}°)")
            else:
                print(f"[ServoController] Moved to {angle}°")

    def move_left(self, degrees=45):
        """
        Move servo left (decrease angle) by specified degrees from current position.

        Args:
            degrees (float): Degrees to move left (default: 45)
        """
        new_angle = self.current_angle - degrees
        self.move(new_angle)

    def move_right(self, degrees=45):
        """
        Move servo right (increase angle) by specified degrees from current position.

        Args:
            degrees (float): Degrees to move right (default: 45)
        """
        new_angle = self.current_angle + degrees
        self.move(new_angle)

    def sweep(self, start_angle, end_angle, steps=10, delay=0.1):
        """
        Sweep servo between two angles smoothly.

        Args:
            start_angle (float): Starting angle in degrees
            end_angle (float): Ending angle in degrees
            steps (int): Number of steps for smooth movement (default: 10)
            delay (float): Delay between steps in seconds (default: 0.1)
        """
        start_angle = self._clamp_angle(start_angle)
        end_angle = self._clamp_angle(end_angle)

        step_size = (end_angle - start_angle) / steps

        if self.debug:
            print(f"[ServoController] Sweeping from {start_angle}° to {end_angle}° in {steps} steps")

        for i in range(steps + 1):
            angle = start_angle + (step_size * i)
            self.move(angle)
            sleep(delay)

    def home(self):
        """
        Return servo to home/center position.
        """
        self.move(self.home_angle)
        if self.debug:
            print(f"[ServoController] Returned to home position ({self.home_angle}°)")

    def get_angle(self):
        """
        Get current servo angle.

        Returns:
            float: Current angle in degrees
        """
        return self.current_angle

    def cleanup(self):
        """
        Release GPIO resources safely.
        Should be called before program exit.
        """
        self.servo.close()
        if self.debug:
            print("[ServoController] GPIO resources released")


# Simple test if run directly
if __name__ == "__main__":
    print("=== ServoController Test ===")
    servo = ServoController(gpio_pin=18, home_angle=90, debug=True)

    try:
        print("\n1. Testing move() to 45 degrees...")
        servo.move(45)
        sleep(1)

        print("\n2. Testing move() to 135 degrees...")
        servo.move(135)
        sleep(1)

        print("\n3. Testing home()...")
        servo.home()
        sleep(1)

        print("\n4. Testing move_left(30)...")
        servo.move_left(30)
        sleep(1)

        print("\n5. Testing move_right(60)...")
        servo.move_right(60)
        sleep(1)

        print("\n6. Testing sweep(0, 180)...")
        servo.sweep(0, 180, steps=20, delay=0.05)
        sleep(0.5)

        print("\n7. Returning home...")
        servo.home()
        sleep(1)

        print("\n=== Test Complete ===")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        servo.cleanup()
        print("Servo cleaned up. Exiting.")
