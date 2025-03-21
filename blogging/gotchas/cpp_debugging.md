### for the legacy paypal code, i did the following:

- c/c++
- c/c++ extension pack
- c/c++ themes
- cmake tools

### c_cpp_properties.json
.vscode/c_cpp_properties.json
```
{
    "configurations": [
        {
            "name": "Mac",
            "includePath": [
                "${workspaceFolder}/**",
                "/Users/kkailasnath/projects/genai/legacy_cpp/**"
            ],
            "defines": [],
            "macFrameworkPath": [
                "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks"
            ],
            "compilerPath": "/usr/bin/clang",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "macos-clang-arm64"
        }
    ],
    "version": 4
}
```
### settings.json

{
    "C_Cpp.errorSquiggles": "disabled"
}
It was able to drill-down into the sources.

---
- Clang compiler is recommended for Mac.