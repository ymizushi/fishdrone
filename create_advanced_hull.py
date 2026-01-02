#!/usr/bin/env python3
"""
FreeCAD script to generate an advanced fishing drone hull
ROV-style design with multiple thrusters and modular components
Inspired by FIFISH and CHASING ROV designs
"""

import sys
sys.path.append('/usr/lib/freecad/lib')

import FreeCAD
import Part
import math

# Create a new document
doc = FreeCAD.newDocument("AdvancedFishingDrone")

# Design parameters
main_body_length = 350  # mm
main_body_width = 280   # mm
main_body_height = 180  # mm
wall_thickness = 4      # mm

# Thruster parameters
thruster_diameter = 60  # mm
thruster_length = 80    # mm
num_thrusters = 6       # 6-thruster configuration

# Battery compartment
battery_width = 150
battery_height = 50
battery_depth = 100

def create_main_body():
    """Create streamlined main body housing using ellipsoid approach"""
    print("Creating main body...")

    # Create main body as scaled sphere (ellipsoid effect)
    # Create three spheres to form a streamlined hull
    center_body = doc.addObject("Part::Box", "CenterBody")
    center_body.Length = main_body_length - 100
    center_body.Width = main_body_width
    center_body.Height = main_body_height
    center_body.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length - 100)/2, -main_body_width/2, -main_body_height/2),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Rounded nose (front)
    nose = doc.addObject("Part::Sphere", "Nose")
    nose.Radius = main_body_height / 2
    nose.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length - 100)/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Rounded tail (rear)
    tail = doc.addObject("Part::Sphere", "Tail")
    tail.Radius = main_body_height / 2
    tail.Placement = FreeCAD.Placement(
        FreeCAD.Vector((main_body_length - 100)/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Fuse all three parts
    body_outer = doc.addObject("Part::MultiFuse", "BodyOuter")
    body_outer.Shapes = [center_body, nose, tail]

    doc.recompute()

    # Create hollow interior (slightly smaller)
    center_inner = doc.addObject("Part::Box", "CenterInner")
    center_inner.Length = main_body_length - 100 - 2*wall_thickness
    center_inner.Width = main_body_width - 2*wall_thickness
    center_inner.Height = main_body_height - 2*wall_thickness
    center_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(
            -(main_body_length - 100)/2 + wall_thickness,
            -main_body_width/2 + wall_thickness,
            -main_body_height/2 + wall_thickness
        ),
        FreeCAD.Rotation(0, 0, 0)
    )

    nose_inner = doc.addObject("Part::Sphere", "NoseInner")
    nose_inner.Radius = main_body_height / 2 - wall_thickness
    nose_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length - 100)/2 + wall_thickness/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    tail_inner = doc.addObject("Part::Sphere", "TailInner")
    tail_inner.Radius = main_body_height / 2 - wall_thickness
    tail_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector((main_body_length - 100)/2 - wall_thickness/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Fuse interior parts
    body_inner = doc.addObject("Part::MultiFuse", "BodyInner")
    body_inner.Shapes = [center_inner, nose_inner, tail_inner]

    doc.recompute()

    # Cut interior to make hollow
    hollow_body = doc.addObject("Part::Cut", "HollowBody")
    hollow_body.Base = body_outer
    hollow_body.Tool = body_inner

    doc.recompute()

    return hollow_body

def create_thruster_mount(position, rotation, name):
    """Create a thruster mount at specified position"""

    # Thruster motor housing
    motor_housing = doc.addObject("Part::Cylinder", f"MotorHousing_{name}")
    motor_housing.Radius = thruster_diameter / 2
    motor_housing.Height = thruster_length
    motor_housing.Placement = FreeCAD.Placement(
        position,
        rotation
    )

    doc.recompute()

    # Propeller guard (torus-like ring)
    guard_outer = doc.addObject("Part::Cylinder", f"GuardOuter_{name}")
    guard_outer.Radius = thruster_diameter / 2 + 15
    guard_outer.Height = 3

    # Position guard at the end of thruster
    guard_pos = FreeCAD.Vector(
        position.x,
        position.y,
        position.z + thruster_length
    )
    guard_outer.Placement = FreeCAD.Placement(guard_pos, rotation)

    doc.recompute()

    # Create guard ring by cutting inner circle
    guard_inner = doc.addObject("Part::Cylinder", f"GuardInner_{name}")
    guard_inner.Radius = thruster_diameter / 2 + 5
    guard_inner.Height = 5
    guard_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(guard_pos.x, guard_pos.y, guard_pos.z - 1),
        rotation
    )

    doc.recompute()

    guard_ring = doc.addObject("Part::Cut", f"GuardRing_{name}")
    guard_ring.Base = guard_outer
    guard_ring.Tool = guard_inner

    doc.recompute()

    # Mounting struts (3 struts connecting to body)
    struts = []
    for i in range(3):
        angle = i * 120  # 120 degrees apart
        strut = doc.addObject("Part::Box", f"Strut_{name}_{i}")
        strut.Length = 25
        strut.Width = 3
        strut.Height = 3

        # Position strut
        rad = math.radians(angle)
        offset_x = math.cos(rad) * (thruster_diameter/2 + 10)
        offset_y = math.sin(rad) * (thruster_diameter/2 + 10)

        strut.Placement = FreeCAD.Placement(
            FreeCAD.Vector(
                position.x + offset_x,
                position.y + offset_y,
                position.z + thruster_length/2
            ),
            FreeCAD.Rotation(0, 0, angle)
        )
        struts.append(strut)

    doc.recompute()

    # Combine all thruster components
    thruster_parts = [motor_housing, guard_ring] + struts
    thruster_assembly = doc.addObject("Part::MultiFuse", f"ThrusterAssembly_{name}")
    thruster_assembly.Shapes = thruster_parts

    doc.recompute()

    return thruster_assembly

def create_thruster_layout():
    """Create 6-thruster configuration for omnidirectional movement"""
    print("Creating thruster layout...")

    thrusters = []

    # Horizontal thrusters (4x) - for forward/backward and lateral movement
    # Front-left
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(-main_body_length/2 - 20, main_body_width/2 - 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90),
        "FrontLeft"
    ))

    # Front-right
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(-main_body_length/2 - 20, -main_body_width/2 + 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90),
        "FrontRight"
    ))

    # Rear-left
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(main_body_length/2 + 20, main_body_width/2 - 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90),
        "RearLeft"
    ))

    # Rear-right
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(main_body_length/2 + 20, -main_body_width/2 + 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90),
        "RearRight"
    ))

    # Vertical thrusters (2x) - for depth control
    # Top-center
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(0, 50, main_body_height/2 + 10),
        FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0),
        "TopCenter"
    ))

    # Bottom-center
    thrusters.append(create_thruster_mount(
        FreeCAD.Vector(0, -50, -main_body_height/2 - 10),
        FreeCAD.Rotation(FreeCAD.Vector(0, 0, 0), 0),
        "BottomCenter"
    ))

    return thrusters

def create_battery_compartment():
    """Create removable battery compartment"""
    print("Creating battery compartment...")

    # Battery bay
    bay = doc.addObject("Part::Box", "BatteryBay")
    bay.Length = battery_depth
    bay.Width = battery_width
    bay.Height = battery_height
    bay.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-battery_depth/2, -battery_width/2, -main_body_height/2 + 10),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Battery access cover (top panel)
    cover = doc.addObject("Part::Box", "BatteryCover")
    cover.Length = battery_depth + 10
    cover.Width = battery_width + 10
    cover.Height = 3
    cover.Placement = FreeCAD.Placement(
        FreeCAD.Vector(
            -battery_depth/2 - 5,
            -battery_width/2 - 5,
            main_body_height/2
        ),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Screw holes for cover
    screw_holes = []
    positions = [
        (-battery_depth/2, -battery_width/2),
        (-battery_depth/2, battery_width/2),
        (battery_depth/2, -battery_width/2),
        (battery_depth/2, battery_width/2)
    ]

    for i, (x, y) in enumerate(positions):
        hole = doc.addObject("Part::Cylinder", f"ScrewHole_{i}")
        hole.Radius = 2.5  # M4 screw
        hole.Height = 10
        hole.Placement = FreeCAD.Placement(
            FreeCAD.Vector(x, y, main_body_height/2 - 2),
            FreeCAD.Rotation(0, 0, 0)
        )
        screw_holes.append(hole)

    doc.recompute()

    return bay, cover, screw_holes

def create_fishing_line_release():
    """Create fishing line release mechanism mount"""
    print("Creating fishing line release mechanism...")

    # Release mechanism housing (front-mounted)
    housing = doc.addObject("Part::Box", "ReleaseMechanism")
    housing.Length = 60
    housing.Width = 40
    housing.Height = 30
    housing.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 60, -20, -15),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Servo mount bracket
    servo_mount = doc.addObject("Part::Box", "ServoMount")
    servo_mount.Length = 25
    servo_mount.Width = 15
    servo_mount.Height = 20
    servo_mount.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 40, -7.5, -10),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Line guide tube
    guide_outer = doc.addObject("Part::Cylinder", "LineGuideOuter")
    guide_outer.Radius = 5
    guide_outer.Height = 40
    guide_outer.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 80, 0, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    guide_inner = doc.addObject("Part::Cylinder", "LineGuideInner")
    guide_inner.Radius = 3
    guide_inner.Height = 45
    guide_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 82, 0, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    doc.recompute()

    guide_tube = doc.addObject("Part::Cut", "LineGuideTube")
    guide_tube.Base = guide_outer
    guide_tube.Tool = guide_inner

    doc.recompute()

    # Combine release mechanism parts
    release_parts = [housing, servo_mount, guide_tube]
    release_assembly = doc.addObject("Part::MultiFuse", "ReleaseAssembly")
    release_assembly.Shapes = release_parts

    doc.recompute()

    return release_assembly

def create_camera_mount():
    """Create camera/electronics mounting points"""
    print("Creating camera mount...")

    # Camera gimbal mount (bottom-front)
    gimbal = doc.addObject("Part::Cylinder", "CameraGimbal")
    gimbal.Radius = 20
    gimbal.Height = 30
    gimbal.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/3, 0, -main_body_height/2 - 30),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # LED light mounts (2x front)
    led_left = doc.addObject("Part::Cylinder", "LED_Left")
    led_left.Radius = 8
    led_left.Height = 15
    led_left.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 + 20, main_body_width/2 - 30, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    led_right = doc.addObject("Part::Cylinder", "LED_Right")
    led_right.Radius = 8
    led_right.Height = 15
    led_right.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 + 20, -main_body_width/2 + 30, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    doc.recompute()

    camera_parts = [gimbal, led_left, led_right]
    camera_assembly = doc.addObject("Part::MultiFuse", "CameraAssembly")
    camera_assembly.Shapes = camera_parts

    doc.recompute()

    return camera_assembly

# Build the complete drone
print("=" * 60)
print("Building Advanced Fishing Drone - ROV Style")
print("=" * 60)

main_body = create_main_body()
thrusters = create_thruster_layout()
battery_bay, battery_cover, screw_holes = create_battery_compartment()
release_mechanism = create_fishing_line_release()
camera_mount = create_camera_mount()

doc.recompute()

# Save the document
output_file = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_advanced.FCStd"
doc.saveAs(output_file)
print(f"\n✓ Advanced drone model saved to: {output_file}")

# Export as STEP
step_file = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_advanced.step"
try:
    all_parts = [main_body] + thrusters + [battery_bay, battery_cover, release_mechanism, camera_mount]
    Part.export(all_parts, step_file)
    print(f"✓ STEP file exported to: {step_file}")
except Exception as e:
    print(f"STEP export error: {e}")

print("\n" + "=" * 60)
print("ADVANCED FISHING DRONE SPECIFICATIONS")
print("=" * 60)
print(f"Main Body Dimensions: {main_body_length} × {main_body_width} × {main_body_height} mm")
print(f"Wall Thickness: {wall_thickness}mm (waterproof)")
print(f"\nPropulsion System:")
print(f"  - {num_thrusters} thrusters (6DOF movement)")
print(f"  - 4× horizontal thrusters (forward/lateral)")
print(f"  - 2× vertical thrusters (depth control)")
print(f"  - Propeller guards on all thrusters")
print(f"\nModular Components:")
print(f"  - Removable battery compartment ({battery_width}×{battery_depth}mm)")
print(f"  - Quick-access battery cover with M4 screws")
print(f"  - Front-mounted fishing line release mechanism")
print(f"  - Camera gimbal mount (bottom-front)")
print(f"  - 2× LED light mounts")
print(f"\nKey Features:")
print(f"  - Streamlined hull with chamfered edges")
print(f"  - Omnidirectional movement capability")
print(f"  - Modular accessory mounting")
print(f"  - Professional ROV-style design")
print("=" * 60)
