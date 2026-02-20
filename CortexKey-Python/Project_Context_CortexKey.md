# Project Context: CortexKey (Formerly NeuroAuth)

## 1. Project Overview
* **Project Name:** CortexKey
* **Tagline:** Brainwave-Backed Authentication / The Mind-Driven Master Key
* [cite_start]**Event Context:** Developed for "Hack Your Path (HYP) 7.0" Hackathon[cite: 68].
* [cite_start]**Team Name:** BlackHats[cite: 71].
* **Team Members:**
    * [cite_start]Devesh (CSD 2nd Yr) - Team Lead [cite: 73]
    * [cite_start]Aditya (CSD 2nd Yr) [cite: 74]
    * [cite_start]Sadaf (CSE 1st Yr) [cite: 75]
    * [cite_start]Abhinav (CSE 1st Yr) [cite: 76]
* [cite_start]**Mission:** To create a low-cost (<₹3,000), non-invasive Brain-Computer Interface (BCI) system that uses unique neural signatures for secure, hands-free user authentication[cite: 161, 162].

---

## 2. Problem Statement
Current authentication methods differ significantly in security and usability:
* [cite_start]**Passwords:** Susceptible to phishing, reuse, and brute-force attacks[cite: 85].
* **Static Biometrics (Fingerprint/FaceID):** Rely on immutable physical traits. [cite_start]Once spoofed (lifted fingerprints, deepfakes), the credential is compromised forever[cite: 86, 87].
* [cite_start]**Lack of Continuous Auth:** Systems typically authenticate only at the login screen, leaving the device vulnerable if the user steps away[cite: 88, 89].

---

## 3. The Solution: CortexKey
CortexKey introduces **"Dynamic Neural Authentication"**:
* [cite_start]**Mechanism:** Users perform a specific mental task (e.g., "Hyper-focus" or "Motor Imagery") to generate a unique EEG pattern[cite: 181].
* [cite_start]**Security:** Brainwaves are internal, non-replicable, and dynamic (alive)[cite: 184].
* [cite_start]**Form Factor:** A lightweight, non-medical grade headband using off-the-shelf electronic components[cite: 164].
* [cite_start]**Use Case:** Serves as a high-security **Second Factor (2FA)** for defense, remote exams, and enterprise logins[cite: 170].

---

## 4. Technical Architecture

### 4.1 Hardware Stack (The "Edge" Layer)
* **Sensor (AFE):** **BioAmp EXG Pill** (or Neuphony EXG Synapse). [cite_start]Captures microvolt-level EEG signals[cite: 133, 134, 135].
* **Microcontroller:** **ESP32** or **Arduino Uno R3**. [cite_start]Handles analog-to-digital conversion and data transmission[cite: 137].
* [cite_start]**Electrodes:** Gel-based Ag/AgCl electrodes placed at **Fp1/Fp2** (Frontal Lobe) and **Mastoid** (Reference)[cite: 149, 162].
* [cite_start]**Power:** Isolated **9V Battery** (Crucial for noise reduction and safety from mains voltage)[cite: 138, 140, 162].
* [cite_start]**Connectivity:** Serial/UART[cite: 146].

### 4.2 Software Stack (The "Processing" Layer)
* [cite_start]**Language:** Python 3.8+ (Backend), C++ (Firmware)[cite: 145].
* [cite_start]**Data Acquisition:** **BrainFlow SDK** (Boardshim)[cite: 190].
* [cite_start]**Signal Processing:** **MNE-Python** & **SciPy**[cite: 157, 191].
* [cite_start]**Machine Learning:** **Scikit-learn** (SVM / Decision Tree Classifiers)[cite: 157, 158].

---

## 5. Implementation Pipeline (The "Signal Chain")

1.  [cite_start]**Acquisition:** Raw EEG data stream initiated from the BioAmp EXG Pill via ESP32[cite: 149].
2.  **Preprocessing:**
    * [cite_start]**Notch Filter:** Applied at **50Hz** to eliminate AC power line noise[cite: 150].
    * [cite_start]**Bandpass Filter:** Applied at **5Hz – 30Hz** to isolate Alpha and Beta waves[cite: 150].
3.  **Feature Extraction:**
    * [cite_start]**PSD (Power Spectral Density):** Analyzing the power distribution across frequency bands[cite: 151, 152].
4.  **Authentication:**
    * [cite_start]Data is fed into a lightweight **SVM Classifier**[cite: 153].
    * If `Confidence > Threshold`, the system triggers the Unlock command.

---

## 6. Research & Academic Foundations
The project is grounded in established neuroscience and cryptographic research.

### 6.1 Core Academic Papers
* **Proof of Concept:** *Chuang, J., Nguyen, H., & Sayed, B. (2013). "Cerebrem: A Brain-Computer Interface for User Authentication."*
    * [cite_start]**Relevance:** Demonstrates that specific mental tasks (e.g., imagining movement or singing) can function as secure, private cryptographic keys[cite: 181, 182].
* **Biometric Superiority:** *Gui, Q., Zhan, Z., & Zhu, J. (2014). "A Survey of EEG-based Biometrics for User Authentication."*
    * [cite_start]**Relevance:** Validates brainwaves as high-entropy, non-static identifiers that are superior to spoofable fingerprints[cite: 183, 184].
* **Hardware Viability:** *Ashby, C., et al. (2011). "Low-Cost EEG Based BCI User Identification."*
    * [cite_start]**Relevance:** Scientifically proves that non-medical grade EEG sensors (like the BioAmp EXG Pill) provide sufficient signal fidelity for robust identity verification[cite: 185, 186].
* **Feature Extraction:** *Palaniappan, R. (2004). "Method of Identifying Individuals Using Brain Electrical Activity Features."*
    * [cite_start]**Relevance:** The foundational study establishing **Power Spectral Density (PSD)** as the primary feature for generating a "Neural Signature"[cite: 187, 188].

### 6.2 Technical Frameworks Referenced
* [cite_start]**BrainFlow SDK:** Utilized as the industry-standard API for real-time biosensor data acquisition across open-source hardware[cite: 190].
* [cite_start]**MNE-Python:** Utilized for scientific-grade EEG signal processing, specifically for artifact removal (blinks/jaw clenches) and noise filtering[cite: 191].

---

## 7. Feasibility & Budget
The project is designed for extreme affordability and student accessibility.

| Component | Estimated Cost (INR) |
| :--- | :--- |
| **BioAmp EXG Pill / Sensor** | [cite_start]₹1,500 [cite: 162] |
| **Microcontroller (ESP32)** | [cite_start]₹600 [cite: 162] |
| **Electrodes & Cables** | [cite_start]₹600 [cite: 162] |
| **Power (Battery + Clip)** | [cite_start]₹100 [cite: 162] |
| **Total BOM Cost** | [cite_start]**~₹2,500 - ₹2,900** [cite: 162] |

* [cite_start]**Status:** Prototype buildable within hackathon timeframe (24-48 hours)[cite: 166].
* **Constraints:** Single-channel limitation (Frontal Cortex only); relies on concentration artifacts rather than complex motor imagery.

---

## 8. Strategic Goals
* [cite_start]**Immediate:** Win 1st Prize at HYP 7.0 (Building on 2nd Prize at Internal SIH 2025)[cite: 194].
* **Partnership:** Secure hardware sponsorship from **Neuphony** to upgrade from DIY sensors to a professional headset.
* [cite_start]**Long-term:** Scale into a plug-and-play USB peripheral for secure remote work environments[cite: 121].