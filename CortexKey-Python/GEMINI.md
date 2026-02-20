# CortexKey: Brainwave-Backed Authentication

## Project Overview
**CortexKey** (formerly NeuroAuth) is a low-cost, non-invasive Brain-Computer Interface (BCI) system designed for secure, hands-free user authentication. It uses unique neural signatures (EEG patterns) as a dynamic biometric for high-security Second Factor Authentication (2FA).

- **Tagline:** The Mind-Driven Master Key
- **Core Technology:** Dynamic Neural Authentication (DNA) via EEG (Alpha/Beta wave ratios).
- **Target Platform:** Windows (accessed via WSL/Linux mount).
- **Primary Language:** Python 3.13.

## Technical Architecture
The system follows a "Signal Chain" pipeline:
1.  **Acquisition:** Raw EEG capture using **BioAmp EXG Pill** and **ESP32**.
2.  **Preprocessing:** 50Hz Notch Filter + 5Hz–30Hz Bandpass Filter (isolating Alpha/Beta).
3.  **Feature Extraction:** Power Spectral Density (PSD) analysis.
4.  **Authentication:** **Scikit-learn** (SVM Classifier) comparing live patterns against a trained signature.
5.  **Automation:** **PyAutoGUI** triggers OS-level actions (e.g., login/unlock).

## Environment & Dependencies
The project uses a Python 3.13 virtual environment located at `.venv/`. Key libraries include:
- **Signal Processing:** `mne`, `scipy`, `numpy`, `neurokit2`.
- **Data Acquisition:** `brainflow`, `pylsl`, `pyserial`, `bleak`.
- **Machine Learning:** `scikit-learn`, `pandas`.
- **Interface & Automation:** `Flask`, `pyautogui`, `keyboard`, `chordspy`.

### Key Tool: ChordSpy
The project integrates **ChordSpy**, a Flask-based web interface for:
- Managing USB, WiFi, and BLE connections to BCI devices.
- Monitoring real-time data streams and recording.
- Logging runtime events to `logs/logging.txt`.

## Building and Running
The project is currently in the **Documentation and Environment Setup** phase.

### Running the Interface
To launch the `chordspy` management interface:
```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the chordspy application (if installed in venv)
python -m chordspy.app
```

### Development Commands (Placeholders)
- **Train Model:** `python scripts/train_model.py` (TODO)
- **Authenticate:** `python scripts/authenticate.py` (TODO)
- **Collect Data:** Use the ChordSpy web interface.

## Project Structure
- `Project_Context_CortexKey.md`: Detailed mission, hardware stack, and implementation roadmap.
- `Updated_context.md`: Refined technical details and competitive advantages.
- `logs/logging.txt`: Active runtime logs from the ChordSpy application.
- `.venv/`: Pre-configured environment for BCI development.

## Development Roadmap
1.  **Hardware Calibration:** Wiring BioAmp EXG and ESP32 with isolated 9V power.
2.  **Signal Verification:** Use ChordSpy to confirm EEG signal quality at Fp1/Fp2.
3.  **Data Collection:** Capture "Relaxed" vs. "Focused" mental states.
4.  **Classifier Training:** Train the SVM model on extracted PSD features.
5.  **End-to-End Auth:** Integrate PyAutoGUI for automated OS login.
