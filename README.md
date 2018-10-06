water-agent
===========
A command line program to query water interruption in İstanbul.

Information
-----------

This script queries water interruption info for İstanbul and sends sms if there is an interruption for the given region. It was written with Python3. Sms is sent by using twilio.

Requirements
------------

* pip install -r requirements.txt

Usage
-----

```python
python3 water_agent.py <name of region> <10 digit phone number to receive message>
```
