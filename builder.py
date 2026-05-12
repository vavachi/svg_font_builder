import subprocess
import os
import tempfile
import json
import shutil
from pathlib import Path

def generate_font_and_dart(svg_paths, font_name, class_name, output_dir, progress_callback=None):
    """
    Generates a TrueType font (.ttf) from a list of SVGs and creates a 
    corresponding Flutter Icons class in Dart.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_svg_dir = temp_dir_path / "svgs"
        temp_svg_dir.mkdir()
        temp_output_dir = temp_dir_path / "output"
        temp_output_dir.mkdir()

        if progress_callback:
            progress_callback(f"Copying {len(svg_paths)} SVGs...")
        
        # Copy SVGs to temp dir
        for p in svg_paths:
            path = Path(p)
            if path.exists() and path.suffix.lower() == '.svg':
                shutil.copy(path, temp_svg_dir / path.name)
        
        # Run fantasticon
        if progress_callback:
            progress_callback("Running fantasticon to generate TTF...")
            progress_callback(f"(Using npx fantasticon from {temp_svg_dir})")
        
        cmd = [
            "npx", "-y", "fantasticon",
            str(temp_svg_dir),
            "-o", str(temp_output_dir),
            "-n", font_name,
            "-t", "ttf"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if progress_callback:
                progress_callback("Fantasticon executed successfully.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to generate font structure. Error output: {e.stderr}")
        
        # Parse JSON
        json_file = temp_output_dir / f"{font_name}.json"
        if not json_file.exists():
            raise Exception("Cannot find output mapping JSON from fantasticon. The font building may have failed without throwing an error.")
            
        with open(json_file, 'r') as f:
            mapping = json.load(f)
            
        # Generate Dart Class
        if progress_callback:
            progress_callback("Generating Dart class...")
            
        dart_code = f"""import 'package:flutter/widgets.dart';

class {class_name} {{
  {class_name}._();

  static const String _fontFamily = '{font_name}';
"""
        for icon_name, codepoint in mapping.items():
            # Create a valid dart variable name
            icon_var = icon_name.replace('-', '_').replace(' ', '_').lower()
            # Fantasticon provides codepoint as an integer, sometimes decimal, sometimes hex.
            # Assuming integer dictionary value format like { "icon": 61697 }
            hex_code = hex(codepoint).replace('0x', '')
            dart_code += f"  static const IconData {icon_var} = IconData(0x{hex_code}, fontFamily: _fontFamily);\n"
            
        dart_code += "}\n"
        
        dart_file_path = temp_output_dir / f"{class_name}.dart"
        with open(dart_file_path, "w") as f:
            f.write(dart_code)
            
        # Copy everything to output dir
        if progress_callback:
            progress_callback("Copying output to target directory...")
            
        final_output = Path(output_dir)
        final_output.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(temp_output_dir / f"{font_name}.ttf", final_output / f"{font_name}.ttf")
        shutil.copy(dart_file_path, final_output / f"{class_name}.dart")
        
        if progress_callback:
            progress_callback(f"Successfully generated {font_name}.ttf and {class_name}.dart in {output_dir}")
