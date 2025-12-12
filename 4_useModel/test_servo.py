#!/usr/bin/env python3
"""
test_servo.py
Simple test program for MG90S servo motor
Just run: python3 test_servo.py
"""

# Setup GPIO for Raspberry Pi 5 (required!)
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()
print("[✓] lgpio initialized for Raspberry Pi 5")

from modules.servo_controller import ServoController
import time
import sys


def print_menu(servo):
    """Print the test menu"""
    print("\n" + "=" * 50)
    print("🎮 SERVO TEST PROGRAM")
    print("=" * 50)
    print(f"GPIO Pin: 18")
    print(f"Current Position: {servo.get_angle()}°")
    print()
    print("Choose a test:")
    print("[1] Move to specific angle")
    print("[2] Move left")
    print("[3] Move right")
    print("[4] Sweep animation")
    print("[5] Go to home (90°)")
    print("[6] Run all automatic tests")
    print("[0] Exit")
    print("=" * 50)


def get_valid_angle():
    """Get valid angle input from user (0-180)"""
    while True:
        try:
            angle = int(input("Enter angle (0-180): "))
            if 0 <= angle <= 180:
                return angle
            else:
                print("❌ Must be between 0 and 180!")
        except ValueError:
            print("❌ Please enter a valid number!")
        except KeyboardInterrupt:
            raise


def get_valid_degrees():
    """Get valid degrees input from user"""
    while True:
        try:
            degrees = int(input("Enter degrees: "))
            return degrees
        except ValueError:
            print("❌ Please enter a valid number!")
        except KeyboardInterrupt:
            raise


def test_basic_moves(servo):
    """Test 1: Basic position movements"""
    print("\n" + "🎯" * 25)
    print("📍 TEST 1: Basic Positions")
    print("🎯" * 25)

    print("\n➡️ Moving to 0° (LEFT)...")
    servo.move(0)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(2)

    print("\n➡️ Moving to 90° (CENTER)...")
    servo.move(90)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(2)

    print("\n➡️ Moving to 180° (RIGHT)...")
    servo.move(180)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(2)

    print("\n➡️ Returning to home...")
    servo.home()
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(1)

    print("\n✅ Test 1 Complete!")


def test_left_right(servo):
    """Test 2: Relative movements"""
    print("\n" + "🎯" * 25)
    print("⬅️➡️ TEST 2: Relative Movements")
    print("🎯" * 25)

    print("\n➡️ Starting at home...")
    servo.home()
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(1)

    print("\n➡️ Moving LEFT 45°...")
    servo.move_left(45)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(2)

    print("\n➡️ Moving RIGHT 90°...")
    servo.move_right(90)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(2)

    print("\n➡️ Moving LEFT 45° (back to center)...")
    servo.move_left(45)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(1)

    print("\n✅ Test 2 Complete!")


def test_sweep(servo):
    """Test 3: Sweep animation"""
    print("\n" + "🎯" * 25)
    print("🌊 TEST 3: Sweep Animation")
    print("🎯" * 25)

    print("\n➡️ Sweeping from 0° to 180°...")
    servo.sweep(start_angle=0, end_angle=180, steps=20, delay=0.05)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(1)

    print("\n➡️ Sweeping from 180° to 0°...")
    servo.sweep(start_angle=180, end_angle=0, steps=20, delay=0.05)
    print(f"   Current position: {servo.get_angle()}°")
    time.sleep(1)

    print("\n➡️ Returning to home...")
    servo.home()
    print(f"   Current position: {servo.get_angle()}°")

    print("\n✅ Test 3 Complete!")


def run_all_tests(servo):
    """Run all automatic tests"""
    print("\n" + "🚀" * 25)
    print("Running ALL automatic tests...")
    print("🚀" * 25)

    test_basic_moves(servo)
    time.sleep(2)

    test_left_right(servo)
    time.sleep(2)

    test_sweep(servo)

    print("\n" + "🎉" * 25)
    print("ALL TESTS COMPLETE!")
    print("🎉" * 25)


def interactive_mode(servo):
    """Interactive mode - user controls servo manually"""
    while True:
        try:
            print_menu(servo)
            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                # Move to specific angle
                print("\n📐 Move to specific angle")
                angle = get_valid_angle()
                print(f"➡️ Moving to {angle}°...")
                servo.move(angle)
                print(f"✅ Moved to {servo.get_angle()}°")
                time.sleep(1)

            elif choice == "2":
                # Move left
                print("\n⬅️ Move left")
                degrees = get_valid_degrees()
                print(f"➡️ Moving left {degrees}°...")
                servo.move_left(degrees)
                print(f"✅ Now at {servo.get_angle()}°")
                time.sleep(1)

            elif choice == "3":
                # Move right
                print("\n➡️ Move right")
                degrees = get_valid_degrees()
                print(f"➡️ Moving right {degrees}°...")
                servo.move_right(degrees)
                print(f"✅ Now at {servo.get_angle()}°")
                time.sleep(1)

            elif choice == "4":
                # Sweep
                print("\n🌊 Sweep animation")
                print("Sweep from 0° to 180° and back")
                print("➡️ Sweeping 0° → 180°...")
                servo.sweep(0, 180, steps=30, delay=0.03)
                time.sleep(0.5)
                print("➡️ Sweeping 180° → 0°...")
                servo.sweep(180, 0, steps=30, delay=0.03)
                print(f"✅ Complete! Now at {servo.get_angle()}°")
                time.sleep(1)

            elif choice == "5":
                # Go home
                print("\n🏠 Returning to home position...")
                servo.home()
                print(f"✅ Now at home: {servo.get_angle()}°")
                time.sleep(1)

            elif choice == "6":
                # Run all tests
                run_all_tests(servo)
                input("\nPress Enter to continue...")

            elif choice == "0":
                # Exit
                print("\n👋 Exiting test program...")
                break

            else:
                print("\n❌ Invalid choice! Please enter 0-6")

        except KeyboardInterrupt:
            print("\n\n⛔ Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Continuing...")


def main():
    """Main function"""
    print("\n" + "=" * 50)
    print("🚀 SERVO TEST PROGRAM - MG90S")
    print("=" * 50)
    print()
    print("This program will test your MG90S servo motor")
    print("Make sure your servo is connected to GPIO 18")
    print()
    print("Wiring:")
    print("  Brown wire  → Pin 6 (GND)")
    print("  Red wire    → Pin 2 (5V)")
    print("  Orange wire → Pin 12 (GPIO 18)")
    print("=" * 50)

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            print("\n🎯 Running QUICK TEST mode...\n")
            servo = ServoController(gpio_pin=18, home_angle=90, debug=True)
            try:
                run_all_tests(servo)
            finally:
                servo.cleanup()
            return

        elif sys.argv[1] == "--angle" and len(sys.argv) > 2:
            try:
                angle = int(sys.argv[2])
                if 0 <= angle <= 180:
                    print(f"\n🎯 Moving to {angle}°...\n")
                    servo = ServoController(gpio_pin=18, home_angle=90, debug=True)
                    try:
                        servo.move(angle)
                        print(f"✅ Servo at {servo.get_angle()}°")
                        time.sleep(2)
                    finally:
                        servo.cleanup()
                    return
                else:
                    print("❌ Angle must be 0-180")
                    return
            except ValueError:
                print("❌ Invalid angle value")
                return

        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python3 test_servo.py              # Interactive mode")
            print("  python3 test_servo.py --quick      # Run all tests automatically")
            print("  python3 test_servo.py --angle 90   # Move to specific angle")
            print("  python3 test_servo.py --help       # Show this help")
            return

    # Initialize servo
    print("\n🔧 Initializing servo on GPIO 18...")
    servo = ServoController(
        gpio_pin=18,
        home_angle=90,
        debug=True
    )

    print("✅ Servo initialized!")

    # Run interactive mode
    try:
        print("\n✨ Entering interactive mode...")
        print("   You can control the servo manually")
        print("   Press Ctrl+C anytime to exit\n")
        time.sleep(1)

        interactive_mode(servo)

    except KeyboardInterrupt:
        print("\n\n⛔ Stopped by user (Ctrl+C)")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        # Cleanup
        print("\n🧹 Cleaning up GPIO...")
        servo.cleanup()
        print("✅ Done! Goodbye! 👋\n")


if __name__ == "__main__":
    main()
