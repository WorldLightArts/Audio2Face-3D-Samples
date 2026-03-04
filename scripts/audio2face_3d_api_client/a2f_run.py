#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import asyncio
import os
import sys
from pathlib import Path
import a2f_3d.client.auth
import a2f_3d.client.service
from nvidia_ace.services.a2f_controller.v1_pb2_grpc import A2FControllerServiceStub

# Model Function IDs with and without tongue animation
MODELS = {
    "claire": {
        "with_tongue": "0961a6da-fb9e-4f2e-8491-247e5fd7bf8d",
        "without_tongue": "617f80a7-85e4-4bf0-9dd6-dcb61e886142",
        "config": "config/config_claire.yml"
    },
    "mark": {
        "with_tongue": "8efc55f5-6f00-424e-afe9-26212cd2c630",
        "without_tongue": "cf145b84-423b-4222-bfdd-15bb0142b0fd",
        "config": "config/config_mark.yml"
    },
    "james": {
        "with_tongue": "9327c39f-a361-4e02-bd72-e11b4c9b7b5e",
        "without_tongue": "8082bdcb-9968-4dc5-8705-423ea98b8fc2",
        "config": "config/config_james.yml"
    }
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audio2Face-3D API Client - Simple Interface",
        epilog="Example: python a2f_run.py --audio input.wav --mark --tongue=true")
    
    parser.add_argument("--audio", type=str, required=True, 
                       help="Input audio file (PCM 16-bit WAV)")
    parser.add_argument("--apikey", type=str, default=None,
                       help="NVIDIA API Key (defaults to NVIDIA_API_KEY env var)")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory (defaults to 'results')")
    
    # Model selection (mutually exclusive)
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument("--claire", action="store_true", help="Use Claire model")
    model_group.add_argument("--mark", action="store_true", help="Use Mark model")
    model_group.add_argument("--james", action="store_true", help="Use James model")
    
    # Tongue animation
    parser.add_argument("--tongue", type=str, default="true", 
                       choices=["true", "false"],
                       help="Enable tongue animation (default: true)")
    
    return parser.parse_args()

def get_model_config(args) -> tuple:
    """Returns (model_name, function_id, config_path)"""
    tongue_enabled = args.tongue.lower() == "true"
    
    if args.claire:
        model_name = "claire"
    elif args.mark:
        model_name = "mark"
    else:
        model_name = "james"
    
    model_info = MODELS[model_name]
    function_id = model_info["with_tongue"] if tongue_enabled else model_info["without_tongue"]
    config_path = model_info["config"]
    
    return model_name, function_id, config_path

async def main():
    args = parse_args()
    
    # Get API key from argument or environment variable
    api_key = args.apikey or os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Error: API key not provided. Use --apikey or set NVIDIA_API_KEY environment variable")
        sys.exit(1)
    
    # Validate audio file
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)
    
    # Get model configuration
    model_name, function_id, config_path = get_model_config(args)
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    # Prepare output directory and basename
    output_dir = args.output_dir or "results"
    os.makedirs(output_dir, exist_ok=True)
    
    audio_basename = Path(args.audio).stem  # filename without extension
    model_name_capitalized = model_name.capitalize()
    output_basename = f"{model_name_capitalized}{audio_basename}"
    
    print(f"Processing: {args.audio}")
    print(f"Model: {model_name} (tongue: {args.tongue})")
    print(f"Output directory: {output_dir}")
    print(f"Output basename: {output_basename}")
    print()
    
    # Create gRPC channel
    metadata_args = [("function-id", function_id), ("authorization", "Bearer " + api_key)]
    channel = a2f_3d.client.auth.create_channel(
        uri="grpc.nvcf.nvidia.com:443", 
        use_ssl=True, 
        metadata=metadata_args
    )
    
    stub = A2FControllerServiceStub(channel)
    stream = stub.ProcessAudioStream()
    
    # Process audio
    write = asyncio.create_task(
        a2f_3d.client.service.write_to_stream(stream, config_path, args.audio)
    )
    read = asyncio.create_task(
        a2f_3d.client.service.read_from_stream(stream, output_dir, output_basename)
    )
    
    await write
    await read
    
    print("\nProcessing complete!")
    print(f"Output files saved to: {output_dir}/")
    print(f"  - {output_basename}_animation_frames.json")
    print(f"  - {output_basename}_a2f_smoothed_emotion_output.json")
    print(f"  - {output_basename}_a2f_input_emotions.json")
    print(f"  - {output_basename}_audio.wav")

if __name__ == "__main__":
    asyncio.run(main())
