.. toctree::
   :hidden:

   self
   wyze_sdk.api
   wyze_sdk.models
   wyze_sdk.errors
   wyze_sdk.signature
   wyze_sdk.logging

Getting Started with Wyze SDK
*****************************

A modern Python client for controlling Wyze devices.

Whether you're building a custom app, or integrating into a third-party service like Home Assistant, Wyze Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Feature                        | What its for                                                                                  | Package                            |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Web Client                     | Send data to or query data from Wyze using a variety of device-specific sub-clients.          | ``wyze_sdk.client``                |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Bulb Client                    | Control Wyze Bulb, Wyze Bulb Color, Wyze Bulb White, and Wyze Light Strip                     | ``wyze_sdk.client.bulbs``          |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Entry Sensor Client            | Interact with Wyze Sense Entry Sensors                                                        | ``wyze_sdk.client.entry_sensors``  |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Camera Client                  | Control Wyze Cameras                                                                          | ``wyze_sdk.client.cameras``        |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Event Client                   | Manage Wyze alarm events                                                                      | ``wyze_sdk.client.events``         |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Lock Client                    | Control Wyze Lock and Wyze Lock Keypad                                                        | ``wyze_sdk.client.locks``          |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Motion Sensor Client           | Interact with Wyze Sense Motion Sensors                                                       | ``wyze_sdk.client.motion_sensors`` |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Plug Client                    | Control Wyze Plug and Wyze Plug Outdoor                                                       | ``wyze_sdk.client.plugs``          |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Scale Client                   | Control Wyze Scale                                                                            | ``wyze_sdk.client.scales``         |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Switch Client                  | Control Wyze Switch                                                                           | ``wyze_sdk.client.switches``       |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Thermostat Client              | Control Wyze Thermostat and Wyze Room Sensor                                                  | ``wyze_sdk.client.thermostats``    |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Vacuum Client                  | Control Wyze Robot Vacuum                                                                     | ``wyze_sdk.client.vacuums``        |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Request Signature Verification | Sign outgoing requests for the Wyze API servers.                                              | ``wyze_sdk.signature``             |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Models                         | Pythonic class objects to model Wyze devices.                                                 | ``wyze_sdk.models``                |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+

**Disclaimer: This repository is for non-destructive use only. WyzeLabs is a wonderful company providing excellent devices at a reasonable price. I ask that you do no harm and be civilized.**

**As this repository is entirely reverse-engineered, it may break at any time. If it does, I will fix it to the best of my ability.**

Installation
============

This package supports Python 3.8 and higher. I recommend using `PyPI <https://pypi.python.org/pypi>`_ to install Wyze SDK

.. code-block:: bash

	pip install wyze_sdk

Of course, you can always pull the source code directly into your project:

.. code-block:: bash

	git clone https://github.com/shauntarves/wyze-sdk.git

And then, save a few lines of code as ``./test.py``.

.. code-block:: python

      # test.py
      import sys
      # Load the local source directly
      sys.path.insert(1, "./wyze-sdk")
      # Enable debug logging
      import logging
      logging.basicConfig(level=logging.DEBUG)
      # Verify it works
      import os
      from wyze_sdk import Client
      client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
      api_response = client.api_test()

You can run the code this way.

.. code-block:: bash

   python test.py

Getting Help
============

If you get stuck, I'm here to help. The following are the best ways to get assistance working through your issue:

- `GitHub Issue Tracker <https://github.com/shauntarves/wyze-sdk/issues>`_ for questions, feature requests, bug reports and general discussion related to this package.

.. include:: metadata.rst

.. only:: html 

   Indices and Tables
   ------------------

   * :ref:`genindex`
   * :ref:`search`
