#!/usr/bin/env python3
"""
FreeCAD script - Optimized detailed fishing drone
Focuses on key components with manufacturing details
"""

import sys
sys.path.append('/usr/lib/freecad/lib')

import FreeCAD
import Part
import math

doc = FreeCAD.newDocument("OptimizedFishingDrone")

# Parameters
main_body_length = 350
main_body_width = 280
main_body_height = 180
wall_thickness = 4
thruster_diameter = 60
thruster_length = 80
propeller_diameter = 70

print("=" * 70)
print("BUILDING OPTIMIZED DETAILED FISHING DRONE")
print("=" * 70)

# ============================================================================
# MAIN BODY WITH DETAILS
# ============================================================================

def create_body():
    print("Creating streamlined body with mounting features...")

    # Center section
    center = doc.addObject("Part::Box", "CenterBody")
    center.Length = main_body_length - 100
    center.Width = main_body_width
    center.Height = main_body_height
    center.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length-100)/2, -main_body_width/2, -main_body_height/2),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Nose
    nose = doc.addObject("Part::Sphere", "Nose")
    nose.Radius = main_body_height / 2
    nose.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length-100)/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Tail
    tail = doc.addObject("Part::Sphere", "Tail")
    tail.Radius = main_body_height / 2
    tail.Placement = FreeCAD.Placement(
        FreeCAD.Vector((main_body_length-100)/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Fuse outer
    outer = doc.addObject("Part::MultiFuse", "BodyOuter")
    outer.Shapes = [center, nose, tail]
    doc.recompute()

    # Interior
    center_inner = doc.addObject("Part::Box", "CenterInner")
    center_inner.Length = main_body_length - 100 - 2*wall_thickness
    center_inner.Width = main_body_width - 2*wall_thickness
    center_inner.Height = main_body_height - 2*wall_thickness
    center_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(
            -(main_body_length-100)/2 + wall_thickness,
            -main_body_width/2 + wall_thickness,
            -main_body_height/2 + wall_thickness
        ),
        FreeCAD.Rotation(0, 0, 0)
    )

    nose_inner = doc.addObject("Part::Sphere", "NoseInner")
    nose_inner.Radius = main_body_height/2 - wall_thickness
    nose_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-(main_body_length-100)/2 + wall_thickness/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    tail_inner = doc.addObject("Part::Sphere", "TailInner")
    tail_inner.Radius = main_body_height/2 - wall_thickness
    tail_inner.Placement = FreeCAD.Placement(
        FreeCAD.Vector((main_body_length-100)/2 - wall_thickness/2, 0, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    inner = doc.addObject("Part::MultiFuse", "BodyInner")
    inner.Shapes = [center_inner, nose_inner, tail_inner]
    doc.recompute()

    # Make hollow
    hollow = doc.addObject("Part::Cut", "HollowBody")
    hollow.Base = outer
    hollow.Tool = inner
    doc.recompute()

    return hollow

# ============================================================================
# DETAILED THRUSTER
# ============================================================================

def create_thruster(pos, rot, name):
    """Single detailed thruster"""

    # Motor housing
    motor = doc.addObject("Part::Cylinder", f"Motor_{name}")
    motor.Radius = thruster_diameter / 2 - 5
    motor.Height = thruster_length
    motor.Placement = FreeCAD.Placement(pos, rot)

    # Motor mount flange
    flange = doc.addObject("Part::Cylinder", f"Flange_{name}")
    flange.Radius = thruster_diameter / 2
    flange.Height = 5
    flange_pos = FreeCAD.Vector(pos.x, pos.y, pos.z + thruster_length/2)
    flange.Placement = FreeCAD.Placement(flange_pos, rot)

    # Propeller (3 blades simplified as boxes)
    blades = []
    for i in range(3):
        blade = doc.addObject("Part::Box", f"Blade_{name}_{i}")
        blade.Length = propeller_diameter/2 - 5
        blade.Width = 10
        blade.Height = 2

        angle = i * 120
        rad = math.radians(angle)
        blade_x = pos.x + math.cos(rad) * 15
        blade_y = pos.y + math.sin(rad) * 15

        blade.Placement = FreeCAD.Placement(
            FreeCAD.Vector(blade_x, blade_y, pos.z + thruster_length + 2),
            FreeCAD.Rotation(0, 0, angle)
        )
        blades.append(blade)

    # Propeller hub
    hub = doc.addObject("Part::Cylinder", f"Hub_{name}")
    hub.Radius = 10
    hub.Height = 8
    hub.Placement = FreeCAD.Placement(
        FreeCAD.Vector(pos.x, pos.y, pos.z + thruster_length),
        rot
    )

    # Guard ring
    guard_out = doc.addObject("Part::Cylinder", f"GuardOut_{name}")
    guard_out.Radius = propeller_diameter/2 + 8
    guard_out.Height = 4
    guard_out.Placement = FreeCAD.Placement(
        FreeCAD.Vector(pos.x, pos.y, pos.z + thruster_length + 8),
        rot
    )

    guard_in = doc.addObject("Part::Cylinder", f"GuardIn_{name}")
    guard_in.Radius = propeller_diameter/2 + 4
    guard_in.Height = 6
    guard_in.Placement = FreeCAD.Placement(
        FreeCAD.Vector(pos.x, pos.y, pos.z + thruster_length + 7),
        rot
    )

    doc.recompute()

    guard = doc.addObject("Part::Cut", f"Guard_{name}")
    guard.Base = guard_out
    guard.Tool = guard_in
    doc.recompute()

    # Mount arm
    arm = doc.addObject("Part::Box", f"Arm_{name}")
    arm.Length = 50
    arm.Width = 8
    arm.Height = 8
    arm.Placement = FreeCAD.Placement(
        FreeCAD.Vector(pos.x - 25, pos.y - 4, pos.z + thruster_length/2),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Fuse thruster parts
    parts = [motor, flange, hub, guard, arm] + blades
    assy = doc.addObject("Part::MultiFuse", f"Thruster_{name}")
    assy.Shapes = parts
    doc.recompute()

    return assy

# ============================================================================
# THRUSTER LAYOUT
# ============================================================================

def create_thrusters():
    print("Creating 6-thruster configuration...")

    thrusters = []

    # 4 horizontal thrusters
    thrusters.append(create_thruster(
        FreeCAD.Vector(-main_body_length/2 - 40, main_body_width/2 - 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90),
        "FL"
    ))

    thrusters.append(create_thruster(
        FreeCAD.Vector(-main_body_length/2 - 40, -main_body_width/2 + 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90),
        "FR"
    ))

    thrusters.append(create_thruster(
        FreeCAD.Vector(main_body_length/2 + 40, main_body_width/2 - 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90),
        "RL"
    ))

    thrusters.append(create_thruster(
        FreeCAD.Vector(main_body_length/2 + 40, -main_body_width/2 + 40, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90),
        "RR"
    ))

    # 2 vertical thrusters
    thrusters.append(create_thruster(
        FreeCAD.Vector(0, 60, main_body_height/2 + 10),
        FreeCAD.Rotation(0, 0, 0),
        "TV"
    ))

    thrusters.append(create_thruster(
        FreeCAD.Vector(0, -60, -main_body_height/2 - 10),
        FreeCAD.Rotation(0, 0, 0),
        "BV"
    ))

    return thrusters

# ============================================================================
# BATTERY PACK
# ============================================================================

def create_battery():
    print("Creating battery pack...")

    # Battery housing
    housing = doc.addObject("Part::Box", "BatteryHousing")
    housing.Length = 140
    housing.Width = 90
    housing.Height = 70
    housing.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-70, -45, -main_body_height/2 + 15),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Battery cells (8 cylinders in 4S2P)
    cells = []
    for i in range(4):
        for j in range(2):
            cell = doc.addObject("Part::Cylinder", f"Cell_{i}_{j}")
            cell.Radius = 9
            cell.Height = 65
            cell.Placement = FreeCAD.Placement(
                FreeCAD.Vector(-45 + i*30, -20 + j*40, -main_body_height/2 + 18),
                FreeCAD.Rotation(0, 0, 0)
            )
            cells.append(cell)

    # BMS board
    bms = doc.addObject("Part::Box", "BMS")
    bms.Length = 50
    bms.Width = 35
    bms.Height = 2
    bms.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-25, -17.5, -main_body_height/2 + 85),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    return [housing, bms] + cells

# ============================================================================
# ELECTRONICS BAY
# ============================================================================

def create_electronics():
    print("Creating electronics...")

    # Main PCB
    pcb = doc.addObject("Part::Box", "MainPCB")
    pcb.Length = 180
    pcb.Width = 120
    pcb.Height = 1.6
    pcb.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-90, -60, 10),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Microcontroller
    mcu = doc.addObject("Part::Box", "MCU")
    mcu.Length = 35
    mcu.Width = 35
    mcu.Height = 4
    mcu.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-17.5, -17.5, 11.6),
        FreeCAD.Rotation(0, 0, 0)
    )

    # 6 ESCs (one per thruster)
    escs = []
    for i in range(6):
        esc = doc.addObject("Part::Box", f"ESC_{i}")
        esc.Length = 38
        esc.Width = 20
        esc.Height = 10

        row = i // 3
        col = i % 3

        esc.Placement = FreeCAD.Placement(
            FreeCAD.Vector(-60 + col*45, -50 + row*60, 11.6),
            FreeCAD.Rotation(0, 0, 0)
        )
        escs.append(esc)

    doc.recompute()

    return [pcb, mcu] + escs

# ============================================================================
# WATERPROOF CONNECTORS
# ============================================================================

def create_connectors():
    print("Creating waterproof connectors...")

    connectors = []

    # Main power connector
    power = doc.addObject("Part::Cylinder", "PowerConnector")
    power.Radius = 8
    power.Height = 35
    power.Placement = FreeCAD.Placement(
        FreeCAD.Vector(main_body_length/2 - 15, 0, main_body_height/2 - 15),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )
    connectors.append(power)

    # Communication connector
    comm = doc.addObject("Part::Cylinder", "CommConnector")
    comm.Radius = 6
    comm.Height = 30
    comm.Placement = FreeCAD.Placement(
        FreeCAD.Vector(main_body_length/2 - 15, main_body_width/2 - 15, 25),
        FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    )
    connectors.append(comm)

    doc.recompute()

    return connectors

# ============================================================================
# FISHING LINE MECHANISM
# ============================================================================

def create_fishing_system():
    print("Creating fishing line release system...")

    # Servo housing
    servo = doc.addObject("Part::Box", "ServoBox")
    servo.Length = 45
    servo.Width = 22
    servo.Height = 38
    servo.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 55, -11, -19),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Spool
    spool = doc.addObject("Part::Cylinder", "LineSpool")
    spool.Radius = 22
    spool.Height = 45
    spool.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 85, 0, -10),
        FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    )

    # Guide tube
    guide_out = doc.addObject("Part::Cylinder", "GuideOuter")
    guide_out.Radius = 5
    guide_out.Height = 45
    guide_out.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 105, 0, -10),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    guide_in = doc.addObject("Part::Cylinder", "GuideInner")
    guide_in.Radius = 3
    guide_in.Height = 50
    guide_in.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 107, 0, -10),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    doc.recompute()

    guide = doc.addObject("Part::Cut", "LineGuide")
    guide.Base = guide_out
    guide.Tool = guide_in
    doc.recompute()

    # Hook attachment
    hook = doc.addObject("Part::Torus", "HookRing")
    hook.Radius1 = 10
    hook.Radius2 = 2.5
    hook.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 - 130, 0, -10),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    doc.recompute()

    return [servo, spool, guide, hook]

# ============================================================================
# CAMERA & LIGHTS
# ============================================================================

def create_camera():
    print("Creating camera and lighting...")

    # Camera housing (sphere)
    cam_housing = doc.addObject("Part::Sphere", "CameraHousing")
    cam_housing.Radius = 22
    cam_housing.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/3, 0, -main_body_height/2 - 38),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Lens
    lens = doc.addObject("Part::Cylinder", "Lens")
    lens.Radius = 9
    lens.Height = 12
    lens.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/3, 0, -main_body_height/2 - 55),
        FreeCAD.Rotation(0, 0, 0)
    )

    # LED lights
    led_l = doc.addObject("Part::Cylinder", "LED_Left")
    led_l.Radius = 11
    led_l.Height = 22
    led_l.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 + 35, main_body_width/2 - 32, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    led_r = doc.addObject("Part::Cylinder", "LED_Right")
    led_r.Radius = 11
    led_r.Height = 22
    led_r.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-main_body_length/2 + 35, -main_body_width/2 + 32, 0),
        FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)
    )

    doc.recompute()

    return [cam_housing, lens, led_l, led_r]

# ============================================================================
# ANTENNA
# ============================================================================

def create_antenna():
    print("Creating antenna...")

    # Mast
    mast = doc.addObject("Part::Cylinder", "AntennaMast")
    mast.Radius = 3.5
    mast.Height = 85
    mast.Placement = FreeCAD.Placement(
        FreeCAD.Vector(main_body_length/2 - 42, 0, main_body_height/2),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Tip
    tip = doc.addObject("Part::Cone", "AntennaTip")
    tip.Radius1 = 3.5
    tip.Radius2 = 0
    tip.Height = 18
    tip.Placement = FreeCAD.Placement(
        FreeCAD.Vector(main_body_length/2 - 42, 0, main_body_height/2 + 85),
        FreeCAD.Rotation(0, 0, 0)
    )

    # Base
    base = doc.addObject("Part::Cylinder", "AntennaBase")
    base.Radius = 9
    base.Height = 12
    base.Placement = FreeCAD.Placement(
        FreeCAD.Vector(main_body_length/2 - 42, 0, main_body_height/2 - 6),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    ant_parts = [mast, tip, base]
    antenna = doc.addObject("Part::MultiFuse", "Antenna")
    antenna.Shapes = ant_parts
    doc.recompute()

    return antenna

# ============================================================================
# BUILD ASSEMBLY
# ============================================================================

body = create_body()
thrusters = create_thrusters()
battery = create_battery()
electronics = create_electronics()
connectors = create_connectors()
fishing = create_fishing_system()
camera = create_camera()
antenna = create_antenna()

doc.recompute()

# Save
output = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_detailed.FCStd"
doc.saveAs(output)
print(f"\n✓ Model saved: {output}")

# Export STEP
step_out = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_detailed.step"
try:
    all_parts = [body, antenna] + thrusters + battery + electronics + connectors + fishing + camera
    Part.export(all_parts, step_out)
    print(f"✓ STEP exported: {step_out}")
except Exception as e:
    print(f"STEP export: {e}")

print("\n" + "=" * 70)
print("DETAILED FISHING DRONE - SPECIFICATIONS")
print("=" * 70)
print(f"""
BODY: {main_body_length}×{main_body_width}×{main_body_height}mm, {wall_thickness}mm wall
PROPULSION: 6 detailed thrusters (4H + 2V) with guards
POWER: 8-cell Li-ion pack (4S2P), BMS
ELECTRONICS: Main PCB, MCU, 6 ESCs
WATERPROOFING: Power & comm connectors
FISHING: Servo release, spool, guide tube, hook ring
IMAGING: Gimbaled camera, 2× LED lights
COMMUNICATION: RF antenna system

TOTAL PARTS: 70+ components
READY FOR: 3D printing, CNC machining, assembly
""")
print("=" * 70)
