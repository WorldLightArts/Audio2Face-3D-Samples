#!/usr/bin/env python3
"""
Map NVIDIA Audio2Face ARKit blendshapes to custom character shape keys.
Reorder the JSON animation data to match the target character's shape key order.
"""

import json
from pathlib import Path

# Your character's shape keys in order (from Blender)
CHARACTER_SHAPE_KEYS = [
    "browLowerL",
    "browLowerR",
    "innerBrowRaiserL",
    "innerBrowRaiserR",
    "outerBrowRaiserL",
    "outerBrowRaiserR",
    "eyesLookLeft",
    "eyesLookRight",
    "eyesLookUp",
    "eyesLookDown",
    "eyesCloseL",
    "eyesCloseR",
    "eyesUpperLidRaiserL",
    "eyesUpperLidRaiserR",
    "squintL",
    "squintR",
    "cheekRaiserL",
    "cheekRaiserR",
    "cheekPuffL",
    "cheekPuffR",
    "noseWrinklerL",
    "noseWrinklerR",
    "jawDrop",
    "jawDropLipTowards",
    "jawThrust",
    "jawSlideLeft",
    "jawSlideRight",
    "mouthSlideLeft",
    "mouthSlideRight",
    "dimpleL",
    "dimpleR",
    "lipCornerPullerL",
    "lipCornerPullerR",
    "lipCornerDepressorL",
    "lipCornerDepressorR",
    "lipStretcherL",
    "lipStretcherR",
    "upperLipRaiserL",
    "upperLipRaiserR",
    "lowerLipDepressorL",
    "lowerLipDepressorR",
    "chinRaiser",
    "lipPressor",
    "pucker",
    "funneler",
    "lipSuck",
]

# ARKit blendshapes in NVIDIA's order (indices 0-51, excluding head/tongue at 52-70)
ARKIT_BLENDSHAPES = [
    "EyeBlinkLeft",           # 0
    "EyeLookDownLeft",        # 1
    "EyeLookInLeft",          # 2
    "EyeLookOutLeft",         # 3
    "EyeLookUpLeft",          # 4
    "EyeSquintLeft",          # 5
    "EyeWideLeft",            # 6
    "EyeBlinkRight",          # 7
    "EyeLookDownRight",       # 8
    "EyeLookInRight",         # 9
    "EyeLookOutRight",        # 10
    "EyeLookUpRight",         # 11
    "EyeSquintRight",         # 12
    "EyeWideRight",           # 13
    "JawForward",             # 14
    "JawLeft",                # 15
    "JawRight",               # 16
    "JawOpen",                # 17
    "MouthClose",             # 18
    "MouthFunnel",            # 19
    "MouthPucker",            # 20
    "MouthLeft",              # 21
    "MouthRight",             # 22
    "MouthSmileLeft",         # 23
    "MouthSmileRight",        # 24
    "MouthFrownLeft",         # 25
    "MouthFrownRight",        # 26
    "MouthDimpleLeft",        # 27
    "MouthDimpleRight",       # 28
    "MouthStretchLeft",       # 29
    "MouthStretchRight",      # 30
    "MouthRollLower",         # 31
    "MouthRollUpper",         # 32
    "MouthShrugLower",        # 33
    "MouthShrugUpper",        # 34
    "MouthPressLeft",         # 35
    "MouthPressRight",        # 36
    "MouthLowerDownLeft",     # 37
    "MouthLowerDownRight",    # 38
    "MouthUpperUpLeft",       # 39
    "MouthUpperUpRight",      # 40
    "BrowDownLeft",           # 41
    "BrowDownRight",          # 42
    "BrowInnerUp",            # 43
    "BrowOuterUpLeft",        # 44
    "BrowOuterUpRight",       # 45
    "CheekPuff",              # 46
    "CheekSquintLeft",        # 47
    "CheekSquintRight",       # 48
    "NoseSneerLeft",          # 49
    "NoseSneerRight",         # 50
    "TongueOut",              # 51
]

# Mapping from ARKit indices to character shape key indices
# This maps: ARKIT_INDEX -> CHARACTER_SHAPE_KEY_INDEX
ARKIT_TO_CHARACTER_MAPPING = {
    # Eyes
    0: 10,   # EyeBlinkLeft -> eyesCloseL
    5: 14,   # EyeSquintLeft -> squintL
    6: 12,   # EyeWideLeft -> eyesUpperLidRaiserL
    7: 11,   # EyeBlinkRight -> eyesCloseR
    12: 15,  # EyeSquintRight -> squintR
    13: 13,  # EyeWideRight -> eyesUpperLidRaiserR
    1: 9,    # EyeLookDownLeft -> eyesLookDown (approximate)
    4: 8,    # EyeLookUpLeft -> eyesLookUp (approximate)
    2: 6,    # EyeLookInLeft -> eyesLookLeft (approximate, inner look)
    3: 6,    # EyeLookOutLeft -> eyesLookLeft (approximate)
    8: 9,    # EyeLookDownRight -> eyesLookDown
    11: 8,   # EyeLookUpRight -> eyesLookUp
    9: 7,    # EyeLookInRight -> eyesLookRight
    10: 7,   # EyeLookOutRight -> eyesLookRight
    
    # Brows
    41: 0,   # BrowDownLeft -> browLowerL
    42: 1,   # BrowDownRight -> browLowerR
    43: 2,   # BrowInnerUp -> innerBrowRaiserL
    44: 4,   # BrowOuterUpLeft -> outerBrowRaiserL
    45: 5,   # BrowOuterUpRight -> outerBrowRaiserR
    
    # Cheeks
    46: 18,  # CheekPuff -> cheekPuffL (use left, or split)
    47: 16,  # CheekSquintLeft -> cheekRaiserL
    48: 17,  # CheekSquintRight -> cheekRaiserR
    
    # Nose
    49: 20,  # NoseSneerLeft -> noseWrinklerL
    50: 21,  # NoseSneerRight -> noseWrinklerR
    
    # Jaw
    17: 22,  # JawOpen -> jawDrop
    14: 24,  # JawForward -> jawThrust
    15: 25,  # JawLeft -> jawSlideLeft
    16: 26,  # JawRight -> jawSlideRight
    
    # Mouth
    19: 43,  # MouthFunnel -> funneler
    20: 42,  # MouthPucker -> pucker
    21: 27,  # MouthLeft -> mouthSlideLeft
    22: 28,  # MouthRight -> mouthSlideRight
    23: 31,  # MouthSmileLeft -> lipCornerPullerL
    24: 32,  # MouthSmileRight -> lipCornerPullerR
    25: 33,  # MouthFrownLeft -> lipCornerDepressorL
    26: 34,  # MouthFrownRight -> lipCornerDepressorR
    27: 29,  # MouthDimpleLeft -> dimpleL
    28: 30,  # MouthDimpleRight -> dimpleR
    29: 35,  # MouthStretchLeft -> lipStretcherL
    30: 36,  # MouthStretchRight -> lipStretcherR
    31: 40,  # MouthRollLower -> lowerLipDepressorL
    32: 38,  # MouthRollUpper -> upperLipRaiserL
    35: 31,  # MouthPressLeft -> lipCornerPullerL (reuse)
    36: 32,  # MouthPressRight -> lipCornerPullerR (reuse)
    37: 40,  # MouthLowerDownLeft -> lowerLipDepressorL
    38: 41,  # MouthLowerDownRight -> lowerLipDepressorR
    39: 38,  # MouthUpperUpLeft -> upperLipRaiserL
    40: 39,  # MouthUpperUpRight -> upperLipRaiserR
    51: 44,  # TongueOut -> lipSuck (placeholder)
}

def convert_a2f_json_to_character(input_json_path, output_json_path=None):
    """
    Convert NVIDIA's 71-blendshape ARKit JSON to character's custom shape key order.
    
    Args:
        input_json_path: Path to the input JSON from Audio2Face-3D
        output_json_path: Path for output JSON
    """
    
    if output_json_path is None:
        input_path = Path(input_json_path)
        output_json_path = input_path.parent / f"{input_path.stem}_character{input_path.suffix}"
    
    print(f"Loading: {input_json_path}")
    with open(input_json_path, 'r') as f:
        data = json.load(f)
    
    weight_mat = data.get('weightMat', [])
    print(f"Original: {len(weight_mat)} frames with {len(weight_mat[0]) if weight_mat else 0} weights per frame")
    print(f"Target shape keys: {len(CHARACTER_SHAPE_KEYS)}\n")
    
    # Reorder each frame according to the mapping
    reordered_weight_mat = []
    
    for frame_weights in weight_mat:
        # Create a new frame with character's shape key order
        new_frame = [0.0] * len(CHARACTER_SHAPE_KEYS)
        
        # Map ARKit values to character shape keys
        for arkit_idx, char_idx in ARKIT_TO_CHARACTER_MAPPING.items():
            if arkit_idx < len(frame_weights) and char_idx < len(new_frame):
                new_frame[char_idx] = frame_weights[arkit_idx]
        
        reordered_weight_mat.append(new_frame)
    
    # Create output data
    output_data = {
        "weightMat": reordered_weight_mat,
        "shapeKeys": CHARACTER_SHAPE_KEYS,  # Include the shape key names for reference
    }
    
    print(f"Saving to: {output_json_path}")
    with open(output_json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Converted: {len(reordered_weight_mat)} frames with {len(CHARACTER_SHAPE_KEYS)} weights per frame")
    print(f"\nShape key mapping applied:")
    print("  ARKit Index -> Character Shape Key (Index -> Name)")
    for arkit_idx in sorted(ARKIT_TO_CHARACTER_MAPPING.keys()):
        char_idx = ARKIT_TO_CHARACTER_MAPPING[arkit_idx]
        print(f"  [{arkit_idx:2d}] {ARKIT_BLENDSHAPES[arkit_idx]:<20} -> [{char_idx:2d}] {CHARACTER_SHAPE_KEYS[char_idx]}")
    
    print(f"\n✓ Output file ready!")
    return str(output_json_path)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python convert_to_character_shapekeys.py <input_json_file> [output_json_file]")
        print("\nExample:")
        print("  python convert_to_character_shapekeys.py MarkMark_neutral_animation_frames.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        convert_a2f_json_to_character(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
