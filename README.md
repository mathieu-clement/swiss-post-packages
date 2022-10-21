# Swiss Post Packages

## Description

Currently this is just a little bit of code to download the list of packages from the [Swiss Post](https://www.post.ch)
website and parse them to Python objects.

Eventually I'd like to integrate this into a Home Assistant component. It could be fun to see if packages
are expected on the current day or following days, and maybe merge data from multiple people, 
create automations with this information, etc.

## Available Data

At the moment the following information is available:

  - Package ID
  - Sender name
  - Delivery status (in transit or delivered; more to be implemented as I discover them)
  - Delivery date (expected or actually delivered)
  - Tracking URL


The tracking URL can be used to fetch additional information about parcels such as the size, 
weight, whether they fit in the mailbox, and even a picture.

## Implementation Details

There are existing Home Assistant integrations for this kind of thing, but they rely on parsing your e-mails
and I'm not a big fan of that from a security and technical perspective.

Ideally I'd have used only the requests Python library and kept cookies in memory, but it proved
a little too time consuming for this proof-of-concept so I went with Selenium, opening a headless browser
(Firefox), logging in, and downloading the parcel data as JSON and then converting that to Python objects.

The Selenium web driver (Firefox) is installed automatically.

## Installation

Create a virtual environment and install required packages:

```bash
python -m venv venv
pip install -r requirements.txt
```

Eventually, depending on how this gets deployed, I'll make it either installable in HACS (Home Assistant
Community Store) or through Docker.

Create a `credentials.py` file with the following content:

```python
EMAIL = '<YOUR SWISS ID EMAIL ADDRESS>'
PASSWORD = '<YOUR PASSWORD>'
```

Similarly here, depending on how this gets deployed, this is likely to change in the future.

## Usage

Run with:

```bash
. ./venv/bin/activate
python app.py
```

of course right now it's at the very early stages, so just take a look at `app.py` if you want to use it
in your project as-is.

## License

>Swiss Post Packages - Scrapes parcels from the post.ch website
>Copyright (C) 2022 Mathieu Clément
>
>This program is free software: you can redistribute it and/or modify
>it under the terms of the GNU General Public License as published by
>the Free Software Foundation, either version 3 of the License, or
>(at your option) any later version.
>
>This program is distributed in the hope that it will be useful,
>but WITHOUT ANY WARRANTY; without even the implied warranty of
>MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
>GNU General Public License for more details.

See [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/) for a copy of the GNU General Public License.
