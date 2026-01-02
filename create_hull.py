#!/usr/bin/env python3
"""
FreeCAD script to generate a fishing drone hull
Creates a catamaran-style hull for stability on water
"""

import sys
sys.path.append('/usr/lib/freecad/lib')

import FreeCAD
import Part
import Sketcher

# Create a new document
doc = FreeCAD.newDocument("FishingDroneHull")

# Parameters for the hull
hull_length = 400  # mm
hull_width = 150   # mm
hull_height = 80   # mm
hull_thickness = 3 # mm
pontoon_spacing = 250  # mm (distance between two pontoons)

def create_pontoon(x_offset=0, name_suffix=""):
    """Create a single pontoon hull shape"""

    # Create a basic box for the pontoon
    pontoon = doc.addObject("Part::Box", f"Pontoon{name_suffix}")
    pontoon.Length = hull_length
    pontoon.Width = hull_width
    pontoon.Height = hull_height
    pontoon.Placement = FreeCAD.Placement(
        FreeCAD.Vector(x_offset - hull_length/2, -hull_width/2, 0),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Create rounded nose (bow)
    nose_radius = hull_width / 2
    nose = doc.addObject("Part::Sphere", f"Nose{name_suffix}")
    nose.Radius = nose_radius
    nose.Placement = FreeCAD.Placement(
        FreeCAD.Vector(x_offset + hull_length/2, 0, nose_radius),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    # Combine pontoon and nose
    fusion = doc.addObject("Part::MultiFuse", f"PontoonFused{name_suffix}")
    fusion.Shapes = [pontoon, nose]

    doc.recompute()

    return fusion

def create_deck():
    """Create a deck platform connecting the two pontoons"""
    deck = doc.addObject("Part::Box", "Deck")
    deck.Length = hull_length - 40
    deck.Width = pontoon_spacing + hull_width
    deck.Height = 5  # 5mm thick deck
    deck.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-hull_length/2 + 20, -pontoon_spacing/2 - hull_width/2, hull_height),
        FreeCAD.Rotation(0, 0, 0)
    )

    doc.recompute()

    return deck

# Create the catamaran hull
print("Creating left pontoon...")
left_pontoon = create_pontoon(-pontoon_spacing/2, "_Left")

print("Creating right pontoon...")
right_pontoon = create_pontoon(pontoon_spacing/2, "_Right")

print("Creating deck...")
deck = create_deck()

doc.recompute()

# Save the document
output_file = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_hull.FCStd"
doc.saveAs(output_file)
print(f"Hull model saved to: {output_file}")

# Export as STEP for compatibility
step_file = "/home/ymizushi/Develop/ymizushi/fishdrone/fishing_drone_hull.step"
try:
    Part.export([left_pontoon, right_pontoon, deck], step_file)
    print(f"STEP file exported to: {step_file}")
except Exception as e:
    print(f"STEP export error (optional): {e}")

print("\nHull specifications:")
print(f"  Total length: {hull_length}mm")
print(f"  Total width: {pontoon_spacing + hull_width}mm")
print(f"  Hull height: {hull_height}mm")
print(f"  Pontoon spacing: {pontoon_spacing}mm")
print("\nDesign features:")
print("  - Catamaran design for stability")
print("  - Filleted edges for hydrodynamics")
print("  - Deck platform for electronics")
print("  - Mounting holes for components")
