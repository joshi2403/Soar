<!--
    DO NOT MANUALLY EDIT THIS FILE
    THIS FILE IS AUTOMATICALLY GENERATED WITH resilient-sdk codegen
-->

# SentinelOne: Get Hash Reputation

## Function - SentinelOne: Get Hash Reputation

### API Name
`sentinelone_get_hash_reputation`

### Output Name
`None`

### Message Destination
`fn_sentinelone`

### Pre-Processing Script
```python
inputs.sentinelone_hash = artifact.value
```

### Post-Processing Script
```python

note = u"<b>SentinelOne: Get Hash Reputation: </b><br>"
content = results.get("content")
inputs = results.get("inputs")
hash_value = inputs.get("sentinelone_hash")
if content:
  data = content.get("data")
  if data:
    rank = data.get("rank")
    note = u"{0} Hash <b>{1}</b> has rank: <b>{2}</b>".format(note, hash_value, rank)
  else:
    note = u"{0} No data returned from function.".format(note)
else:
  note = u"{0} No content data returned from function.".format(note)
  
incident.addNote(helper.createRichText(note))
```

---

