# e91-simulation

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

This project simulates the **E91 quantum key distribution (QKD) protocol**, proposed by Artur Ekert in 1991. The protocol uses entangled photon pairs and Bell's inequality to establish a secure cryptographic key between two distant parties (Alice and Bob), while also detecting the presence of an eavesdropper (Eve).

The simulation is written in Python and implements two distinct scenarios:

- **Ideal scenario** – No noise, no eavesdropping. Demonstrates the theoretical correctness of the protocol.
- **Interruption scenario** – Introduces an eavesdropper or realistic noise. Shows how the protocol detects intrusions via violation of Bell's inequality.

By running these simulations, the project **proves the availability and security of the E91 protocol** under both ideal and compromised conditions.

## Features

- Pure Python implementation (no external dependencies required)
- Clear separation between ideal and interrupted execution paths
- Calculation of CHSH (Clauser–Horne–Shimony–Holt) inequality value
- Detection threshold to identify eavesdropping attempts
- Configurable parameters (number of qubit pairs, noise level, etc.)

## Installation

Clone the repository and navigate into the project folder:

```bash
git clone https://github.com/zhaomumu666/e91-simulation.git
cd e91-simulation
