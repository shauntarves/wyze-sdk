# Python Wyze SDK
A modern Python client for controlling Wyze devices.

[![pypi package][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Python Version][python-version]][pypi-url]

Whether you're building a custom app, or integrating into a third-party service like Home Assistant, Wyze Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

The **Python Wyze SDK** allows interaction with:

- `wyze_sdk.bulbs`: for controlling Wyze Bulb and Wyze Bulb Color
- `wyze_sdk.vacuums`: for controlling Wyze Robot Vacuum
- `wyze_sdk.scales`: for controlling Wyze Scale
- `wyze_sdk.plugs`: for controlling Wyze Plug and (coming soon) Wyze Plug Outdoor
- `wyze_sdk.motion_sensors`: for interacting with Wyze Motion Sensor
- `wyze_sdk.entry_sensors`: for interacting with Wyze Entry Sensor

**Disclaimer: This repository is for fun only. WyzeLabs is a wonderful company providing excellent devices at a reasonable price. I ask that you do no harm and be civilized.**

**As this repository is entirely reverse-engineered, it may break at any time. If it does, I will fix it to the best of my ability, but feel free to file a GitHub issue or patch yourself and submit a pull request.**

### Requirements

---

This library requires Python 3.8 and above. If you're unsure how to check what version of Python you're on, you can check it using the following:

> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`

```bash
python --version

-- or --

python3 --version
```

### Installation

We recommend using [PyPI][pypi] to install the Wyze Developer Kit for Python.

```bash
$ pip install wyze_sdk
```

### Basic Usage of the Web Client

---

Wyze does not provide a Web API that gives you the ability to build applications that interact with Wyze devices. This Development Kit is a reverse-engineered, module-based wrapper that makes interaction with that API possible. We have a basic example here with some of the more common uses but you are encouraged to explore the full range of methods available to you.

