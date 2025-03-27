- Add the following file named `.clangd` 
- Adding this file resolved the dependency issue in vscode.
```
## .clangd contents
CompileFlags: 
  Add: [-I/Users/kkailasnath/projects/cpp/cpp_dep]
```
- Here I am including the dependency in the compileflags.

Then in `c_cpp_properties.json`, do the following: 
```
{
  "configurations": [
    {
      "name": "macos-clang-arm64",
      "includePath": [
        "${workspaceFolder}/**",
        "/Users/kkailasnath/projects/cpp/cpp_dep" 
      ],
      "compilerPath": "/usr/bin/clang",
      "cStandard": "${default}",
      "cppStandard": "${default}",
      "intelliSenseMode": "macos-clang-arm64",
      "compilerArgs": [
        ""
      ]
    }
  ],
  "version": 4
}
```

in `launch.json`, 
```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "(lldb) Launch",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/main",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}",
      "environment": [],
      "externalConsole": false,
      "MIMode": "lldb"
    },
    {
      "name": "C/C++ Runner: Debug Session",
      "type": "lldb",
      "request": "launch",
      "args": [],
      "cwd": "${workspaceFolder}",
      "program": "${workspaceFolder}/main"
    },
  ]
}
```

In `tasks.json`, 
```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build C++ Project",
            "type": "shell",
            "command": "clang++",
            "args": [
                "main.cpp",
                "/Users/kkailasnath/projects/cpp/cpp_dep/math_utils.cpp",
                "-o",
                "main",
                "-g",
                "-stdlib=libc++",
                "-I/Library/Developer/CommandLineTools/usr/include/c++/v1",
                "-I/Users/kkailasnath/projects/cpp/cpp_dep/"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": ["$gcc"],
            "detail": "Build task for compiling C++ project"
        },
        {
            "label": "Run C++ Program",
            "type": "shell",
            "command": "./main",
            "group": {
                "kind": "test",
                "isDefault": true
            },
            "problemMatcher": [],
            "detail": "Build task for running C++ project"
        }
    ]
}
```