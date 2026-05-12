# SVG Font Builder for Flutter

A desktop application built with Python and PyQt6 that converts a collection of SVG icons into a custom TrueType font (`.ttf`) and dynamically generates a corresponding Dart class (`Icons.dart`) for seamless integration into Flutter projects.

## How It Works

This application orchestrates the complex mathematical process of SVG path conversion by acting as a Python GUI wrapper around `fantasticon`. 
1. **User Interface**: The user drag-and-drops SVGs or entire directories into the PyQt6 window.
2. **Intermediate Environment**: Behind the scenes, the scripts copy your SVGs into a temporary, isolated workspace.
3. **Engine Processing**: Python initiates a background system subprocess executing `npx fantasticon`. This parses the SVGs, generates font tables (glyphs, outlines, character mappings), and produces a binary `.ttf` file alongside a JSON codepoint dictionary.
4. **Code Generation**: The python script reads the newly generated JSON metadata and algorithmically generates a standard Flutter `IconData` class (`.dart`) mapping variable names to their new unicodes.
5. **Output**: Finally, the TrueType font and the Dart integration file are moved into your targeted output directory.

## Prerequisites

- **Python 3.10+**
- **Node.js & npm** (required to run `npx fantasticon` under the hood)

## Setup & Setup

1. Clone or download this project folder.
2. Open a terminal within the root directory of the project.
3. Set up your Python Virtual Environment and install the PyQt6 UI framework:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `.\venv\Scripts\activate`
pip install -r requirements.txt
```

## Usage

To launch the GUI Application from the source code, run:
```bash
python3 main.py
```

### From the Interface:
1. Click **Add SVGs** to select individual files, or **Add Folder** to automatically import all `.svg` files located in a directory. Alternatively, you can Drag & Drop them straight into the list.
2. Set your **Font Family Name** (e.g., `AppIcons`). This dictates the name of the generated `.ttf` file and the `fontFamily` argument used internally in Flutter.
3. Set your **Flutter Class Name** (e.g., `AppIcons`). This dictates the name of the exported `.dart` file and the static class you will call strictly in your Flutter app (e.g., `AppIcons.my_svg_name`).
4. Select an **Output Directory** where you want the resulting files to be exported.
5. Click **Generate Flutter Font**. The built-in logger will keep you updated on the status!

## Building Standalone Executables

If you do not want to run the application through the command line or share the tool with a non-developer, you can bundle it into a standalone executable. The provided build scripts parse the Python dependencies using `PyInstaller`.

### Building for Mac (.app)
Ensure your virtual environment is active, then execute:
```bash
./build.sh
```
A native Mac Application bundle will drop into the freshly generated `dist/` folder, which you can simply double-click!

### Building for Windows (.exe)
**Important**: A Windows executable *must* be built on a Windows operating system.
Drop the project codebase into your Windows environment, open the Command Prompt, and run:
```cmd
build.bat
```
A standalone executable will drop into the newly generated `dist\` folder!

## Integration with Flutter

To use your generated `.ttf` font file and `.dart` class in your Flutter project, follow these steps:

### 1. Add the TTF to your project
Copy the generated `.ttf` file into your Flutter project's `assets/fonts/` directory.

### 2. Update `pubspec.yaml`
Declare the custom font inside your Flutter app's `pubspec.yaml` file so the framework can load it. Make sure the `family` name matches exactly what you inputted as the **Font Family Name** in the Builder Tool:

```yaml
flutter:
  fonts:
    - family: AppIcons
      fonts:
        - asset: assets/fonts/AppIcons.ttf
```

### 3. Import and use the Class
Copy the generated `.dart` class into your source lib `lib/` directory. Then, simply import it and drop the icons into your `Icon()` widgets!

```dart
import 'package:your_app/icons/AppIcons.dart';
import 'package:flutter/material.dart';

class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Icon(
      AppIcons.my_svg_icon_name, 
      size: 24, 
      color: Colors.blue
    );
  }
}
```
