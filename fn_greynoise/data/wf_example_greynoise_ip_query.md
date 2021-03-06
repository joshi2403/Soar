<!--
    DO NOT MANUALLY EDIT THIS FILE
    THIS FILE IS AUTOMATICALLY GENERATED WITH resilient-circuits codegen
-->

# Example: GreyNoise IP Query

## Function - GreyNoise IP Query

### API Name
`greynoise_ip_query`

### Output Name
`None`

### Message Destination
`fn_greynoise`

### Pre-Processing Script
```python
inputs.greynoise_value = artifact.value
```

### Post-Processing Script
```python
if results['success']:
  note = u"""<div>Seen: <b>{}</b></div>
<div>IP: <b>{}</b></div>
<div>Classification: <b>{}</b></div>
<div>Tags: <b>{}</b></div>
<div>First seen: <b>{}</b></div>
<div>Last seen: <b>{}</b></div>
<div>Reverse DNS: <b>{}</b></div>""".format('True' if results.content['seen'] else 'False', results.content['ip'], results.content.get('classification'), 
                                          str(results.content.get('tags')), 
                                          results.content.get('first_seen'), results.content.get('last_seen'),
                                          results.content.get('metadata', {})['rdns'])
  if results.content.get('code'):
    code_lookup = { 
      "0x00": "Never Observed",
      "0x01": "Observed",
      "0x02": "Observed, but incomplete",
      "0x03": "Adjacent to another observed",
      "0x04": "Reserved",
      "0x05": "Commonly Spoofed",
      "0x06": "Noise",
      "0x07": "Invalid setting",
      "0x08": "Not observed in last 60 days"
    }
    note = note + u"<div>Code: <b>{}</b></div>".format(code_lookup[results.content['code']])
  incident.addNote(helper.createRichText(note))
else:
  incident.addNote(str(results.content))

"""
{'content': {u'code': u'0x01', u'ip': u'23.129.64.159', u'noise': True}, 'success': True}
{
  'content': {
    u'classification': u'malicious',
    u'tags': [
      u'CHINANET SSH Bruteforcer',
      u'Go SSH Scanner',
      u'HNAP Crawler',
      u'HTTP Alt Scanner',
      u'Nmap',
      u'SSH Bruteforcer',
      u'SSH Scanner',
      u'SSH Worm',
      u'TLS/SSL Crawler',
      u'Tor',
      u'VNC Bruteforcer',
      u'VNC Scanner',
      u'Web Crawler',
      u'Web Scanner'
    ],
    u'ip': u'23.129.64.159',
    u'actor': u'unknown',
    u'raw_data': {
      u'web': {
        u'paths': [
          u'/HNAP1/'
        ],
        u'useragents': [
          u'Mozilla/5.0 (Windows NT 5.1; rv:9.0.1) Gecko/20100101 Firefox/9.0.1'
        ]
      },
      u'ja3': [
        {
          u'port': 443,
          u'fingerprint': u'95d6f221c32953590c3a85cbee0d9e61'
        },
        {
          u'port': 8443,
          u'fingerprint': u'97f7c02d49f8b261f4b7157e38945459'
        },
        {
          u'port': 10000,
          u'fingerprint': u'0d85f6adde9dc6aa98804d6cfa2f90c1'
        },
        {
          u'port': 8080,
          u'fingerprint': u'ac8cb78cabd066a9ce1e90848a0ba5d9'
        }
      ],
      u'scan': [
        {
          u'protocol': u'TCP',
          u'port': 22
        },
        {
          u'protocol': u'TCP',
          u'port': 443
        },
        {
          u'protocol': u'TCP',
          u'port': 1027
        },
        {
          u'protocol': u'TCP',
          u'port': 1028
        },
        {
          u'protocol': u'TCP',
          u'port': 5000
        },
        {
          u'protocol': u'TCP',
          u'port': 5800
        },
        {
          u'protocol': u'TCP',
          u'port': 5900
        },
        {
          u'protocol': u'TCP',
          u'port': 5905
        },
        {
          u'protocol': u'TCP',
          u'port': 8000
        },
        {
          u'protocol': u'TCP',
          u'port': 8080
        },
        {
          u'protocol': u'TCP',
          u'port': 8443
        },
        {
          u'protocol': u'TCP',
          u'port': 10000
        },
        {
          u'protocol': u'TCP',
          u'port': 32768
        },
        {
          u'protocol': u'TCP',
          u'port': 41798
        },
        {
          u'protocol': u'TCP',
          u'port': 43719
        },
        {
          u'protocol': u'TCP',
          u'port': 49152
        },
        {
          u'protocol': u'TCP',
          u'port': 49153
        },
        {
          u'protocol': u'TCP',
          u'port': 49154
        },
        {
          u'protocol': u'TCP',
          u'port': 49157
        }
      ]
    },
    u'seen': True,
    u'first_seen': u'2019-04-23',
    u'metadata': {
      u'category': u'business',
      u'city': u'Seattle',
      u'tor': True,
      u'country': u'United States',
      u'country_code': u'US',
      u'organization': u'Emerald Onion',
      u'os': u'FreeBSD',
      u'asn': u'AS396507'
    },
    u'last_seen': u'2019-10-10'
  },
  'success': True
}
"""
```

---

