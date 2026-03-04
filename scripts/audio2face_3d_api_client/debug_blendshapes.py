#!/usr/bin/env python3
"""
Debug script to analyze which blendshapes are being used in the animation output.
"""

import json
import sys

# Standard ARKit blendshape order (52 total)
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

def analyze_json_file(json_path):
    """Analyze which blendshapes are being animated."""
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    weight_mat = data['weightMat']
    num_frames = len(weight_mat)
    num_weights_per_frame = len(weight_mat[0]) if num_frames > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"Animation Analysis: {json_path}")
    print(f"{'='*80}")
    print(f"Number of frames: {num_frames}")
    print(f"Weights per frame: {num_weights_per_frame}")
    print(f"Standard ARKit blendshapes: {len(ARKIT_BLENDSHAPES)}")
    print(f"Extra/unknown blendshapes: {num_weights_per_frame - len(ARKIT_BLENDSHAPES)}")
    
    # Find all indices that have non-zero values anywhere in the animation
    active_indices = set()
    max_weights_by_index = {}
    
    for frame in weight_mat:
        for idx, weight in enumerate(frame):
            if weight > 0:
                active_indices.add(idx)
                if idx not in max_weights_by_index:
                    max_weights_by_index[idx] = weight
                else:
                    max_weights_by_index[idx] = max(max_weights_by_index[idx], weight)
    
    print(f"\nActive blendshape indices (with non-zero weights): {len(active_indices)}")
    print(f"Indices: {sorted(active_indices)}\n")
    
    print(f"{'Index':<6} {'Max Weight':<12} {'Blendshape Name':<35} {'Type':<15}")
    print("-" * 80)
    
    for idx in sorted(active_indices):
        max_weight = max_weights_by_index[idx]
        if idx < len(ARKIT_BLENDSHAPES):
            name = ARKIT_BLENDSHAPES[idx]
            bs_type = "ARKit"
        else:
            name = f"UNKNOWN[{idx - len(ARKIT_BLENDSHAPES)}]"
            bs_type = "Unknown"
        
        print(f"{idx:<6} {max_weight:<12.4f} {name:<35} {bs_type:<15}")
    
    # Analyze which ARKit categories are being used
    print(f"\n{'='*80}")
    print("Summary by category:")
    print(f"{'='*80}")
    
    categories = {
        "Eye": list(range(0, 14)),
        "Jaw": list(range(14, 18)),
        "Mouth": list(range(18, 41)),
        "Brow": list(range(41, 46)),
        "Cheek": list(range(46, 49)),
        "Nose": list(range(49, 51)),
        "Tongue": [51],
    }
    
    for cat_name, cat_indices in categories.items():
        active_in_cat = [i for i in cat_indices if i in active_indices]
        if active_in_cat:
            print(f"\n{cat_name}:")
            for idx in active_in_cat:
                print(f"  - [{idx}] {ARKIT_BLENDSHAPES[idx]}: {max_weights_by_index[idx]:.4f}")
    
    # Check for unknown blendshapes
    unknown_indices = [i for i in active_indices if i >= len(ARKIT_BLENDSHAPES)]
    if unknown_indices:
        print(f"\nUnknown/Extra blendshapes (outside ARKit spec):")
        for idx in unknown_indices:
            print(f"  - [{idx}] UNKNOWN_BLENDSHAPE_{idx - len(ARKIT_BLENDSHAPES)}: {max_weights_by_index[idx]:.4f}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    json_file = r"c:\Users\USER\Documents\GitHub\Audio2Face-3D-Samples\scripts\audio2face_3d_api_client\results\MarkClaire_neutral_animation_frames.json"
    analyze_json_file(json_file)
