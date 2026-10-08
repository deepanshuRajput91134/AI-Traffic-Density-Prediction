# Computer Vision Module — Vehicle Detection & Telemetry Pipeline

## Architecture Overview
The Computer Vision module bridges physical traffic monitoring hardware (CCTV cameras, video feeds, and surveillance imagery) with the AI Machine Learning density prediction engine.

```
+--------------------+      +--------------------+      +---------------------+
| Traffic Camera /   | ---> | Frame Extraction & | ---> | Multi-Class Vehicle |
| CCTV Video Feed    |      | Preprocessing      |      | Detection (OpenCV)  |
+--------------------+      +--------------------+      +---------------------+
                                                                   |
                                                                   v
+--------------------+      +--------------------+      +---------------------+
| Smart City UI &    | <--- | Dijkstra Graph     | <--- | ML Traffic Density  |
| Route Guidance     |      | Route Optimization |      | Prediction (Model)  |
+--------------------+      +--------------------+      +---------------------+
```

## Supported Vehicle Classes
* 🚗 **Car** (Standard passenger automobile, Weight: 1.0)
* 🏍️ **Motorcycle** (Two-wheeler transport, Weight: 0.5)
* 🚌 **Bus** (Public transit vehicle, Weight: 2.5)
* 🚚 **Truck** (Heavy commercial goods transport, Weight: 3.0)

## macOS CPU Compatibility
To ensure 100% reliable performance during college project viva without requiring NVIDIA CUDA or heavy cloud accelerators, the detector is optimized for local CPU execution via OpenCV.
