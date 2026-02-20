# Project Context: CortexKey (Brainwave-Backed Authentication)

## 1. Project Overview
* **Project Identity:** CortexKey (Formerly NeuroAuth).
* **Mission:** Creating a low-cost, non-invasive Brain-Computer Interface (BCI) for secure, hands-free authentication.
* **Context:** Developed for the "Hack Your Path (HYP) 7.0" Hackathon.
* **Team:** BlackHats (Devesh, Aditya, Sadaf, Abhinav).

## 2. The Problem Statement
* **Static Biometric Vulnerability:** Fingerprints and FaceID are immutable; if compromised, they cannot be changed.
* **Credential Insecurity:** Standard passwords are susceptible to phishing and brute-force attacks.
* **Lack of Liveness:** Traditional systems struggle to distinguish between a real user and a replica (deepfakes or lifted prints).

## 3. The Technical Solution
CortexKey uses a dynamic "Neural Signature" for authentication:
* **Mechanism:** Users perform a specific mental task (e.g., hyper-focus) to generate unique EEG patterns.
* **Security:** Brainwaves are internal, invisible, and inherently provide proof-of-liveness.

## 4. Hardware Architecture

### 4.1 Microcontroller (MCU)
* **Choice:** **ESP32 (NodeMCU Development Board)**.
* **Rationale:** Features 12-bit ADC resolution for high-fidelity signal capture, dual-core processing for simultaneous data acquisition and transmission, and built-in Bluetooth for wireless isolation.

### 4.2 Sensing Layer
* **Primary Option:** **BioAmp EXG Pill** (Analog Front-End).
* **Alternative:** **Neuphony EXG Synapse**.
* **Custom Engineering:** A discrete breadboard implementation using a **TL074 Quad Op-Amp** chip, 4-stage instrumentation amplification, and active noise cancellation (Driven Right Leg).
* **Electrodes:** 3 gel-based Ag/AgCl electrodes placed at Fp1/Fp2 (Forehead) and a Reference on the mastoid.

### 4.3 Power & Safety
* **Isolation:** Powered by an isolated **9V Battery** to eliminate 50Hz mains noise and ensure user safety.

## 5. Software & Processing Pipeline

### 5.1 Software Stack
* **Firmware:** C++ (Arduino IDE) for ESP32 data streaming.
* **Backend:** Python 3.8+ for signal processing and automation.
* **Key Libraries:** `BrainFlow` (acquisition), `MNE-Python` & `SciPy` (filtering), `Scikit-learn` (ML/SVM), and `PyAutoGUI` (automation).
* **Monitoring:** Chords Web or Backyard Brains Spike Recorder for real-time visualization.

### 5.2 Processing Chain
1. **Acquisition:** Raw EEG capture from the frontal lobe.
2. **Preprocessing:** Application of a **50Hz Notch Filter** and a **5Hz–30Hz Bandpass Filter**.
3. **Extraction:** Analysis of Power Spectral Density (PSD) to identify Beta/Alpha wave ratios.
4. **Authentication:** A lightweight **SVM Classifier** matches the live pattern against the trained neural signature.

## 6. Research Foundations
The project is grounded in four foundational academic pillars:
* **Cerebrem (Chuang et al., 2013):** Proof that mental tasks act as cryptographic keys.
* **EEG Biometrics (Gui et al., 2014):** Validation of brainwaves as high-entropy, non-static identifiers.
* **Low-Cost Viability (Ashby et al., 2011):** Evidence that non-medical grade sensors provide sufficient fidelity for ID verification.
* **Neural Signatures (Palaniappan, 2004):** Established PSD as the primary feature for biometric identification.

## 7. Implementation Roadmap
* **Phase 1:** Hardware wiring and isolated power setup.
* **Phase 2:** Firmware flashing and signal verification via Chords Web.
* **Phase 3:** Python-based digital filtering (Notch/Bandpass).
* **Phase 4:** Calibration and data collection (Relaxed vs. Focused states).
* **Phase 5:** Training the SVM Classifier/Threshold logic.
* **Phase 6:** End-to-end automation of the OS login via PyAutoGUI.

## 8. Competitive Advantage
* **Revocability:** Unlike fingerprints, if a "neural password" is compromised, the user can simply train a new mental task.
* **Quantum Resistance:** Brainwaves provide high-entropy biological chaos that is resistant to mathematical cracking methods used by quantum computers.
* **Affordability:** Total Bill of Materials (BOM) is estimated at **~₹2,500 - ₹2,900**, significantly lower than commercial hardware passkeys.