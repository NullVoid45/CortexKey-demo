#!/usr/bin/env python3
"""
CortexKey: Brainwave Authenticator (ESP32 -> Encrypted Signature)

Collects EEG-like signals from an ESP32 over serial, computes frequency-band
features, and produces an encrypted brainwave signature for authentication.

Features:
- 50Hz Notch Filter & 5Hz-30Hz Bandpass Filter
- Welch's Method for PSD estimation
- Strided sliding window processing
- AES-GCM encryption with HKDF-SHA256 key derivation
- Robust serial handling with reconnection logic
- Comprehensive logging and error handling

Dependencies:
    pip install pyserial numpy scipy cryptography
"""

from __future__ import annotations

import argparse
import base64
import logging
import os
import sys
import time
from collections import deque
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Optional, Tuple

import numpy as np

try:
    import serial
except Exception:  # pragma: no cover
    serial = None  # Checked at runtime

try:
    from scipy import signal
except Exception:  # pragma: no cover
    signal = None  # Checked at runtime

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


DEFAULT_FS = 256.0
DEFAULT_WINDOW = 512
DEFAULT_STEP = 128
DEFAULT_BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 12.0),
    "beta": (12.0, 30.0),
    "gamma": (30.0, 45.0),
}
NOTCH_FREQ = 50.0
NOTCH_Q = 30.0
BANDPASS_LOW = 5.0
BANDPASS_HIGH = 30.0
BUTTERWORTH_ORDER = 4


def setup_logging(
    log_dir: Path, log_filename: str = "brainwave_auth.log"
) -> logging.Logger:
    """Configure logging to both file and stdout."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_filename

    logger = logging.getLogger("CortexKey.Auth")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s: %(message)s",
        datefmt="%Y%m%d_%H%M%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


@contextmanager
def managed_serial(
    port: str, baud: int, timeout: float = 1.0
) -> Generator[serial.Serial, None, None]:
    """Context manager for serial port with automatic cleanup."""
    if serial is None:
        raise RuntimeError("pyserial is not installed. Run: pip install pyserial")

    ser = serial.Serial(port, baud, timeout=timeout)
    try:
        yield ser
    finally:
        if ser.is_open:
            ser.close()


@contextmanager
def managed_file(path: Path, mode: str = "a") -> Generator:
    """Context manager for file handles with automatic cleanup."""
    f = open(path, mode, encoding="utf-8")
    try:
        yield f
    finally:
        f.close()


class BrainwaveProcessor:
    """Processes EEG data and generates encrypted signatures."""

    def __init__(
        self,
        fs: float,
        passphrase: str,
        bands: dict[str, tuple[float, float]] = DEFAULT_BANDS,
        notch_freq: float = NOTCH_FREQ,
        notch_q: float = NOTCH_Q,
        bandpass: tuple[float, float] = (BANDPASS_LOW, BANDPASS_HIGH),
        butter_order: int = BUTTERWORTH_ORDER,
    ):
        self._validate_inputs(fs, passphrase, bands)
        self.fs = fs
        self.passphrase = passphrase
        self.bands = bands
        self.notch_freq = notch_freq
        self.notch_q = notch_q
        self.bandpass = bandpass
        self.butter_order = butter_order

        self._notch_coeffs = self._compute_notch_coeffs()
        self._bandpass_coeffs = self._compute_bandpass_coeffs()
        self.key, self.salt = self._derive_key(passphrase)

    def _validate_inputs(self, fs: float, passphrase: str, bands: dict) -> None:
        """Validate processor parameters."""
        if fs <= 0:
            raise ValueError(f"Sampling frequency must be positive, got {fs}")
        if not passphrase or not passphrase.strip():
            raise ValueError("Passphrase cannot be empty")
        if not bands:
            raise ValueError("Frequency bands cannot be empty")
        for name, (low, high) in bands.items():
            if low >= high:
                raise ValueError(
                    f"Band '{name}': low ({low}) must be less than high ({high})"
                )
            if low < 0 or high > fs / 2:
                raise ValueError(f"Band '{name}': frequencies must be in [0, fs/2]")

    def _compute_notch_coeffs(self) -> Tuple[np.ndarray, np.ndarray]:
        """Compute IIR notch filter coefficients."""
        if signal is None:
            raise RuntimeError("scipy.signal is required for filtering")
        return signal.iirnotch(self.notch_freq, self.notch_q, self.fs)

    def _compute_bandpass_coeffs(self) -> Tuple[np.ndarray, np.ndarray]:
        """Compute IIR bandpass filter coefficients."""
        if signal is None:
            raise RuntimeError("scipy.signal is required for filtering")
        nyquist = self.fs / 2
        low = self.bandpass[0] / nyquist
        high = self.bandpass[1] / nyquist
        return signal.butter(self.butter_order, [low, high], btype="band")

    def _derive_key(self, passphrase: str) -> Tuple[bytes, bytes]:
        """Derive 32-byte AES key from passphrase using HKDF-SHA256."""
        salt = os.urandom(16)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"brainwave-auth-v1",
            backend=default_backend(),
        )
        return hkdf.derive(passphrase.encode("utf-8")), salt

    def apply_filters(self, data: np.ndarray) -> np.ndarray:
        """Apply Notch (50Hz) and Bandpass (5-30Hz) filters to data."""
        if signal is None:
            raise RuntimeError("scipy.signal is required for filtering")

        b_notch, a_notch = self._notch_coeffs
        data = signal.filtfilt(b_notch, a_notch, data, axis=0)

        b_bp, a_bp = self._bandpass_coeffs
        data = signal.filtfilt(b_bp, a_bp, data, axis=0)

        return data

    def compute_features(self, window_data: np.ndarray) -> np.ndarray:
        """Compute relative band powers using Welch's method."""
        if signal is None:
            raise RuntimeError("scipy.signal is required for PSD estimation")

        if window_data.size == 0:
            return np.zeros(len(self.bands), dtype=np.float32)

        filtered = self.apply_filters(window_data)

        if filtered.ndim > 1:
            filtered = np.mean(filtered, axis=1)

        nperseg = min(len(filtered), 256)
        freqs, psd = signal.welch(filtered, self.fs, nperseg=nperseg)

        feature_vector = []
        for band_name, (low, high) in self.bands.items():
            idx = (freqs >= low) & (freqs <= high)
            if np.any(idx):
                band_power = np.trapz(psd[idx], freqs[idx])
            else:
                band_power = 0.0
            feature_vector.append(band_power)

        return np.array(feature_vector, dtype=np.float32)

    def encrypt_signature(self, features: np.ndarray) -> str:
        """Encrypt feature vector using AES-GCM."""
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, features.tobytes(), None)
        payload = self.salt + nonce + ciphertext
        return base64.urlsafe_b64encode(payload).decode("ascii")

    def verify_signature(self, signature: str, features: np.ndarray) -> bool:
        """Verify that a signature matches the given features."""
        try:
            payload = base64.urlsafe_b64decode(signature.encode("ascii"))
            salt = payload[:16]
            nonce = payload[16:28]
            ciphertext = payload[28:]

            key, _ = self._derive_key(self.passphrase, salt)
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted == features.tobytes()
        except Exception:
            return False


class SerialCollector:
    """Collects EEG data from ESP32 over serial connection."""

    def __init__(
        self,
        port: str,
        baud: int,
        window_size: int,
        step_size: int,
        logger: logging.Logger,
    ):
        self._validate_inputs(port, baud, window_size, step_size)
        self.port = port
        self.baud = baud
        self.window_size = window_size
        self.step_size = step_size
        self.logger = logger
        self.ser: Optional[serial.Serial] = None

    def _validate_inputs(
        self, port: str, baud: int, window_size: int, step_size: int
    ) -> None:
        """Validate collector parameters."""
        if not port:
            raise ValueError("Serial port cannot be empty")
        if baud <= 0:
            raise ValueError(f"Baud rate must be positive, got {baud}")
        if window_size <= 0:
            raise ValueError(f"Window size must be positive, got {window_size}")
        if step_size <= 0:
            raise ValueError(f"Step size must be positive, got {step_size}")
        if step_size > window_size:
            raise ValueError(
                f"Step size ({step_size}) cannot exceed window size ({window_size})"
            )

    def connect(self) -> None:
        """Establish serial connection with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.ser = serial.Serial(
                    self.port,
                    self.baud,
                    timeout=1.0,
                    write_timeout=1.0,
                )
                self.logger.info(f"Connected to {self.port} at {self.baud} baud")
                return
            except serial.SerialException as e:
                self.logger.warning(
                    f"Connection attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
        self.logger.error(
            f"Failed to connect to {self.port} after {max_retries} attempts"
        )
        raise ConnectionError(f"Could not connect to serial port {self.port}")

    def disconnect(self) -> None:
        """Close serial connection if open."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.info("Serial connection closed")

    def parse_line(self, line: str) -> Optional[Tuple[float, List[float]]]:
        """Parse a line from ESP32 into timestamp and samples."""
        line = line.strip()
        if not line:
            return None

        for prefix in ("DATA:", "DATA|"):
            if line.upper().startswith(prefix):
                line = line[len(prefix) :]
                break

        try:
            parts = [x.strip() for x in line.split(",") if x.strip()]
            if len(parts) < 2:
                return None
            timestamp = float(parts[0])
            samples = [float(x) for x in parts[1:]]
            return timestamp, samples
        except (ValueError, IndexError):
            return None

    def stream(
        self,
        processor: BrainwaveProcessor,
        output_file: Optional[Path] = None,
    ) -> None:
        """Stream EEG data, process windows, and generate signatures."""
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Not connected. Call connect() first.")

        buffer: deque[List[float]] = deque(maxlen=self.window_size)
        samples_since_last = 0
        out_handle = None

        try:
            if output_file:
                out_handle = open(output_file, "a", encoding="utf-8")
                self.logger.info(f"Writing signatures to {output_file}")

            while True:
                if not self.ser.is_open:
                    self.logger.warning("Serial port closed. Attempting reconnect...")
                    time.sleep(2)
                    self.connect()
                    continue

                try:
                    line = self.ser.readline()
                except serial.SerialException as e:
                    self.logger.error(f"Read error: {e}")
                    self.connect()
                    continue

                if not line:
                    continue

                parsed = self.parse_line(line.decode("ascii", errors="ignore"))
                if parsed is None:
                    continue

                timestamp, samples = parsed
                buffer.append(samples)
                samples_since_last += 1

                ready = (
                    len(buffer) == self.window_size
                    and samples_since_last >= self.step_size
                )

                if ready:
                    data = np.array(buffer)
                    features = processor.compute_features(data)
                    signature = processor.encrypt_signature(features)

                    ts = int(time.time())
                    self.logger.info(f"Signature: {signature[:32]}...")
                    print(f"[{ts}] {signature}")

                    if out_handle:
                        out_handle.write(f"{ts},{signature}\n")
                        out_handle.flush()

                    samples_since_last = 0

        except KeyboardInterrupt:
            self.logger.info("Streaming stopped by user")
        finally:
            self.disconnect()
            if out_handle:
                out_handle.close()


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if args.window <= 0:
        raise argparse.ArgumentTypeError(
            f"--window must be positive, got {args.window}"
        )
    if args.step <= 0:
        raise argparse.ArgumentTypeError(f"--step must be positive, got {args.step}")
    if args.step > args.window:
        raise argparse.ArgumentTypeError(
            f"--step ({args.step}) cannot exceed --window ({args.window})"
        )
    if args.fs <= 0:
        raise argparse.ArgumentTypeError(f"--fs must be positive, got {args.fs}")
    if not args.passphrase or not args.passphrase.strip():
        raise argparse.ArgumentTypeError("--passphrase cannot be empty")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="CortexKey Brainwave Authenticator - Collect EEG from ESP32, "
        "compute features, generate encrypted signatures",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Serial baud rate",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help="Window size in samples for feature extraction",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=DEFAULT_STEP,
        help="Step size in samples for sliding window",
    )
    parser.add_argument(
        "--fs",
        type=float,
        default=DEFAULT_FS,
        help="Sampling frequency in Hz",
    )
    parser.add_argument(
        "--passphrase",
        required=True,
        help="Passphrase for key derivation",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="File to append signatures (optional)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs"),
        help="Directory for log files",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging to console",
    )
    return parser


def main() -> None:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_args(args)
    except argparse.ArgumentTypeError as e:
        parser.print_usage()
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    logger = setup_logging(args.log_dir)

    if serial is None:
        logger.error("pyserial not installed. Run: pip install pyserial")
        sys.exit(1)
    if signal is None:
        logger.error("scipy not installed. Run: pip install scipy")
        sys.exit(1)

    try:
        processor = BrainwaveProcessor(
            fs=args.fs,
            passphrase=args.passphrase,
        )
        collector = SerialCollector(
            port=args.port,
            baud=args.baud,
            window_size=args.window,
            step_size=args.step,
            logger=logger,
        )
        collector.connect()
        collector.stream(processor, args.output)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
