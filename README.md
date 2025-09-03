# ComfyUI-Arduino

**ComfyUI-Arduino** aims to bridge the gap between ComfyUI's powerful generative AI workflows and the physical world through Arduino. This project allows you to design, code, and interact with Arduino boards directly from your ComfyUI nodes, opening up possibilities for AI-driven robotics, physical generative art, interactive installations, and more.

### Core Features (Roadmap)

Here are the initial goals for the project:

- [ ] **Self-contained Installer Node:** Automatically downloads and manages `arduino-cli` locally. No manual setup required from the user, ensuring a smooth "all-in-one" experience.
- [ ] **Dynamic Upload Node:** Visually build logic with nodes, which will then generate, compile, and upload a custom sketch to your connected Arduino board.
- [ ] **Real-time Communication:** Implement a standard sketch and corresponding nodes to send live data (e.g., servo angles, LED colors) from ComfyUI to a running Arduino without re-uploading.
- [ ] **Example Workflows:** Provide simple, functional examples to help users get started quickly.

### Future Vision

Ideas for the long-term development of the project:

- [ ] **Arduino Library Management:** A node to automatically install required libraries for your sketch using `arduino-cli`.
- [ ] **High-Level Hardware Nodes:** Easy-to-use nodes for common components (servos, sensors, NeoPixel LEDs, etc.) that abstract away the low-level code.
- [ ] **In-Workflow C++ Editor:** A dedicated node to write or paste raw Arduino (C++) code directly within ComfyUI.
- [ ] **Full Sketch Export:** An option to export the generated C++ code and a list of its dependencies, allowing it to be used outside of ComfyUI.

### Installation

1.  Navigate to your `ComfyUI/custom_nodes/` directory.
2.  Clone this repository: `git clone https://github.com/Juste-Leo2/ComfyUI-Arduino.git`
3.  Restart ComfyUI. The necessary dependencies, including `arduino-cli`, should be installed automatically on the first run.

### Contributing

This project is currently in the idea and planning phase. Contributions are highly welcome! Whether it's feature ideas, bug reports, code improvements, or pull requests, your help is greatly appreciated to bring this project to life.

### License

This project is licensed under the Apache 2.0 License.