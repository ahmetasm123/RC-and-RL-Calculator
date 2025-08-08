# RC and RL Calculator

A Python GUI application for exploring series **RL** (resistor–inductor) and **RC** (resistor–capacitor) circuits. It computes key electrical parameters and can plot voltage/current waveforms and phasor diagrams.

## Installation
1. Ensure Python 3.11+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   On Linux you may also need the Tk GUI libraries, e.g. `sudo apt-get install python3-tk`.

## Running the GUI
Launch the calculator with:
```bash
python main.py
```
Alternatively use the module form:
```bash
python -m RC-and-RL-Calculator
```

### GUI Usage
1. Choose **RL** or **RC**.
2. Enter source RMS voltage and resistance.
3. Provide any two of component value (L or C), reactance (X_L or X_C), or frequency.
4. Click **Compute** to calculate derived values such as impedance, phase angle, current and voltages.
5. Use **Plot Waveforms** or **Plot Phasors** to visualise the circuit behaviour.

## Core Functions
### `calculate_derived_reactance_params(component_val, reactance_val, omega, param_type)`
Derives the missing value among component magnitude, reactance and angular frequency for an RL or RC circuit, performing consistency checks on the inputs. Returns a tuple `(component, reactance, omega)`.

### `calculate_series_ac_circuit(V_rms, R, component_val, reactance_val, f, circuit_type)`
Computes parameters for a series RL or RC circuit. Requires the RMS source voltage, resistance and any two of component value, reactance or frequency. Returns a dictionary containing impedance, phase angle, currents and voltages.

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for
coding standards, testing instructions, and the pull request workflow. By
participating in this project you agree to abide by our
[Code of Conduct](CODE_OF_CONDUCT.md).

## License
This project is licensed under the [MIT License](LICENSE).
