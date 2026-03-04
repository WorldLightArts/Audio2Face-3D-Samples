#!/usr/bin/env python3
"""
Convert Audio2Face-3D JSON (71 blendshapes) to FaceIT-compatible JSON (52 ARKit blendshapes)

This script removes the extra head rotation and tongue-specific blendshapes that are not
part of the standard ARKit specification, keeping only indices 0-51.
"""

import json
import sys
from pathlib import Path

def convert_a2f_json_to_faceit(input_json_path, output_json_path=None):
    """
    Convert 71-blendshape JSON to 52-blendshape ARKit JSON for FaceIT compatibility.
    
    Args:
        input_json_path: Path to the input JSON file from Audio2Face-3D
        output_json_path: Path for output JSON (defaults to input filename with _faceit suffix)
    """
    
    # Default output path
    if output_json_path is None:
        input_path = Path(input_json_path)
        output_json_path = input_path.parent / f"{input_path.stem}_faceit{input_path.suffix}"
    
    print(f"Loading: {input_json_path}")
    with open(input_json_path, 'r') as f:
        data = json.load(f)
    
    # Extract weightMat
    weight_mat = data.get('weightMat', [])
    print(f"Original: {len(weight_mat)} frames with {len(weight_mat[0]) if weight_mat else 0} weights per frame")
    
    # Trim each frame to only the first 52 ARKit blendshapes
    # Discard indices 52-70 (head rotation and tongue-specific shapes)
    trimmed_weight_mat = []
    for frame_weights in weight_mat:
        # Keep only the first 52 standard ARKit blendshapes
        trimmed_frame = frame_weights[:52]
        trimmed_weight_mat.append(trimmed_frame)
    
    # Create output data
    output_data = {
        "weightMat": trimmed_weight_mat
    }
    
    # Save to output file
    print(f"Saving to: {output_json_path}")
    with open(output_json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Converted: {len(trimmed_weight_mat)} frames with 52 weights per frame")
    print(f"\nRemoved blendshapes (indices 52-70):")
    print("  - HeadRoll, HeadPitch, HeadYaw")
    print("  - TongueTipUp, TongueTipDown, TongueTipLeft, TongueTipRight")
    print("  - TongueRollUp, TongueRollDown, TongueRollLeft, TongueRollRight")
    print("  - TongueUp, TongueDown, TongueLeft, TongueRight")
    print("  - TongueIn, TongueStretch, TongueWide, TongueNarrow")
    print(f"\nOutput file ready for import into FaceIT!")
    return str(output_json_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_faceit.py <input_json_file> [output_json_file]")
        print("\nExample:")
        print("  python convert_json_to_faceit.py Markfirst_animation_frames.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        convert_a2f_json_to_faceit(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
