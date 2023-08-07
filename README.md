# Python Wyze SDK
A modern Python client for controlling Wyze devices.

[![PyPI version][pypi-image]][pypi-url]
[![Python Version][python-version]][pypi-url]
[![Read the Docs][support-docs]][docs-url]


Whether you're building a custom app, or integrating into a third-party service like Home Assistant, Wyze Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

The **Python Wyze SDK** allows interaction with:

- `wyze_sdk.client.bulbs`: for controlling Wyze Bulb, Wyze Bulb Color, Wyze Bulb White, and Wyze Light Strip
- `wyze_sdk.client.entry_sensors`: for interacting with Wyze Entry Sensor
- `wyze_sdk.client.cameras`: for interacting with Wyze Cameras
- `wyze_sdk.client.events`: for managing Wyze alarm events
- `wyze_sdk.client.locks`: for interacting with Wyze Lock and Wyze Lock Keypad
- `wyze_sdk.client.motion_sensors`: for interacting with Wyze Motion Sensor
- `wyze_sdk.client.plugs`: for controlling Wyze Plug and Wyze Plug Outdoor
- `wyze_sdk.client.scales`: for controlling Wyze Scale
- `wyze_sdk.client.switches`: for controlling Wyze Switch
- `wyze_sdk.client.thermostats`: for controlling Wyze Thermostat and Wyze Room Sensor
- `wyze_sdk.client.vacuums`: for controlling Wyze Robot Vacuum

**Disclaimer: This repository is for non-destructive use only. WyzeLabs is a wonderful company providing excellent devices at a reasonable price. I ask that you do no harm and be civilized.**

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
$ pip install wyze-sdk
```

### Basic Usage of the Web Client

---

Wyze does not provide a Web API that gives you the ability to build applications that interact with Wyze devices. This Development Kit is a reverse-engineered, module-based wrapper that makes interaction with that API possible. We have a few basic examples here with some of the more common uses but you are encouraged to [explore the full range of methods](https://wyze-sdk.readthedocs.io/en/latest/wyze_sdk.api.devices.html) available to you.

#### Authenticating

When performing user "authentication" with an email and password in the Wyze app, the credentials are exchanged for an access token and a refrsh token. These are long strings of the form `lvtx.XXXX`. When using this library, be aware that there are two method for handling authentiation:

##### Obtaining the Token and Storing it for Later Use (Preferred)

It is preferred that users first create an empty `Client` object and use the `login()` method to perform the token exchange.

```python
import os
from wyze_sdk import Client

response = Client().login(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
print(f"access token: {response['access_token']}")
print(f"refresh token: {response['refresh_token']}")
```

The returned values can be stored on disk or as environment variables for use in subsequent calls.

```python
import os
from wyze_sdk import Client

client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])
...
```

##### (Deprecated) Automatically Authenticate Every New Client

This method has been deprecated due to issues with authentication rate limiting. While it is still a perfectly usable approach for testing or performing infrequent client actions, it **is not recommended** if you are scripting with this client library.

```python
import os
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

client = Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])
...
```

##### Wyze API Key/ID Support

Visit the Wyze developer API portal to generate an API ID/KEY: https://developer-api-console.wyze.com/#/apikey/view

```python
import os
from wyze_sdk import Client

response = Client().login(
    email=os.environ['WYZE_EMAIL'],
    password=os.environ['WYZE_PASSWORD'],
    key_id=os.environ['WYZE_KEY_ID'],
    api_key=os.environ['WYZE_API_KEY']
)
...
```

##### Multi-Factor Authentication (2FA) Support

If your Wyze account has multi-factor authentication (2FA) enabled, you may be prompted for your 2FA code when authenticating via either supported method described above. If you wish to automate the MFA interaction, both the `Client` constructor and the `login()` method accept `totp_key` as input. If the TOTP key is provided, the MFA prompt should not appear. Your TOTP key can be obtained during the Wyze 2FA setup process and is the same code that you would typically input into an authenticator app during 2FA setup.

```python
import os
from wyze_sdk import Client

response = Client().login(
  email=os.environ['WYZE_EMAIL'],
  password=os.environ['WYZE_PASSWORD'],
  totp_key=os.environ['WYZE_TOTP_KEY']
)

OR

client = Client(
  email=os.environ['WYZE_EMAIL'],
  password=os.environ['WYZE_PASSWORD'],
  totp_key=os.environ['WYZE_TOTP_KEY']
)
...
```

**Note: This does not work with SMS or email-based MFA.**

#### Listing devices in your Wyze account

One of the most common use-cases is querying device state from Wyze. If you want to access devices you own, or devices shared to you, this method will do both.

```python
import os
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])

try:
    response = client.devices_list()
    for device in client.devices_list():
        print(f"mac: {device.mac}")
        print(f"nickname: {device.nickname}")
        print(f"is_online: {device.is_online}")
        print(f"product model: {device.product.model}")
except WyzeApiError as e:
    # You will get a WyzeApiError if the request failed
    print(f"Got an error: {e}")
```

#### Turning off a switch

Some devices - like cameras, bulbs, and plugs - can be switched on and off. This is done with a simple command and even supports delayed actions via timers.

```python
import os
from datetime import timedelta
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])

try:
  plug = client.plugs.info(device_mac='ABCDEF1234567890')
  print(f"power: {plug.is_on}")
  print(f"online: {plug.is_online}")

  if plug.is_on:
    client.plugs.turn_off(device_mac=plug.mac, device_model=plug.product.model, after=timedelta(hours=3))
  else:
    client.plugs.turn_on(device_mac=plug.mac, device_model=plug.product.model)

    plug = client.plugs.info(device_mac=plug.mac)
    assert plug.is_on is True
except WyzeApiError as e:
    # You will get a WyzeApiError if the request failed
    print(f"Got an error: {e}")
```

#### Setting device properties

Every Wyze device has myriad properties and attributes that can be set in a common, intuitive way.

```python
import os
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])

try:
  bulb = client.bulbs.info(device_mac='ABCDEF1234567890')
  print(f"power: {bulb.is_on}")
  print(f"online: {bulb.is_online}")
  print(f"brightness: {bulb.brightness}")
  print(f"temp: {bulb.color_temp}")
  print(f"color: {bulb.color}")

  client.bulbs.set_brightness(device_mac=bulb.mac, device_model=bulb.product.model, brightness=100)
  client.bulbs.set_color(device_mac=bulb.mac, device_model=bulb.product.model, color='ff00ff')
  client.bulbs.set_color_temp(device_mac=bulb.mac, device_model=bulb.product.model, color_temp=3800)
  
  bulb = client.bulbs.info(device_mac='ABCDEF1234567890')
  assert bulb.brightness == 100
  assert bulb.color == 'ff00ff'
  assert bulb.color_temp == 3800

  client.bulbs.set_away_mode(device_mac=bulb.mac, device_model=bulb.product.model, away_mode=True)

except WyzeApiError as e:
    # You will get a WyzeApiError if the request failed
    print(f"Got an error: {e}")
```

#### Taking actions on devices

Want to unlock your lock, or tell your vacuum to clean certain rooms? Yeah, we got that.

```python
import os
import wyze_sdk
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

client = Client(token=os.environ['WYZE_ACCESS_TOKEN'])

try:
  lock = client.locks.info(device_mac='YD.LO1.abcdefg0123456789abcdefg0123456789')
  if lock is not None:
    print(f"is open: {lock.is_open}")
    print(f"is locked: {lock.is_locked}")

    if not lock.is_locked:
      ## let's try to figure out when it was unlocked
      for record in client.locks.get_records(device_mac='YD.LO1.abcdefg0123456789abcdefg0123456789', since=datetime.now() - timedelta(hours=12)):
        print(f"lock record time: {record.time}")
        print(f"lock record type: {record.type}")
        print(f"lock record source: {record.details.source}")

      ## lock up
      client.locks.lock(device_mac='YD.LO1.abcdefg0123456789abcdefg0123456789')

except WyzeApiError as e:
    # You will get a WyzeApiError if the request failed
    print(f"Got an error: {e}")


try:
  vacuum = client.vacuums.info(device_mac='JA_RO2_ABCDEF123456')

  from wyze_sdk.models.devices import VacuumMode

  # if our vacuum is out sweeping, let's find out where he is and tell him to go home
  if vacuum.mode == VacuumMode.SWEEPING:
    print(f"current position: {vacuum.current_position}")

    client.vacuums.dock(device_mac='JA_RO2_ABCDEF123456', device_model=vacuum.product.model)

  # idle hands are the devil's playground - go clean the kitchen
  elif vacuum.mode == VacuumMode.IDLE:
    # want to see what's going on behind the scenes?
    wyze_sdk.set_stream_logger('wyze_sdk', level=logging.DEBUG)

    client.vacuums.sweep_rooms(device_mac='JA_RO2_ABCDEF123456', room_ids=[room.id for room in vacuum.current_map.rooms if room.name == 'Kitchen'])

except WyzeApiError as e:
    # You will get a WyzeApiError if the request failed
    print(f"Got an error: {e}")
```

<!-- Markdown links -->

[pypi-image]: https://badge.fury.io/py/wyze-sdk.svg
[pypi-url]: https://pypi.org/project/wyze-sdk/
[python-version]: https://img.shields.io/pypi/pyversions/wyze-sdk.svg
[pypi]: https://pypi.org/
[gh-issues]: https://github.com/shauntarves/wyze-sdk/issues
[support-docs]: https://img.shields.io/badge/support-docs-brightgreen
[docs-url]: https://wyze-sdk.readthedocs.io
