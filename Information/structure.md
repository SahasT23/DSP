dsp_edu_app/
├── CMakeLists.txt          # Top-level CMake config for building C++ backend
├── README.md               # Instructions for building/running
├── requirements.txt        # Python deps: pybind11, numpy, scipy, matplotlib, tkinter (though tkinter is stdlib)
├── src/                    # C++ source files
│   ├── CMakeLists.txt      # Sub-CMake for src
│   ├── dsp_core.cpp        # Core DSP functions (e.g., DFT, FFT) - <200 lines
│   ├── filters.cpp         # FIR/IIR filter implementations - <200 lines
│   └── bindings.cpp        # pybind11 bindings - <100 lines
├── include/                # C++ headers
│   ├── dsp_core.h          # Headers for dsp_core.cpp
│   └── filters.h           # Headers for filters.cpp
├── python/                 # Python code
│   ├── main.py             # Entry point: Launches GUI - <100 lines
│   ├── gui.py              # GUI layout and event handlers (tkinter) - <300 lines
│   ├── plotter.py          # Handles matplotlib integration and command execution - <150 lines
│   └── chapters.py         # Chapter-specific content (explanations, demos) - <200 lines
└── build/                  # Build directory (git-ignored)