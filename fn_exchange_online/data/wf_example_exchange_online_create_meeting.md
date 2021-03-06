<!--
    DO NOT MANUALLY EDIT THIS FILE
    THIS FILE IS AUTOMATICALLY GENERATED WITH resilient-circuits codegen
-->

# Example: Exchange Online Create Meeting

## Function - Exchange Online: Create Meeting

### API Name
`exchange_online_create_meeting`

### Output Name
`None`

### Message Destination
`fn_exchange_online`

### Pre-Processing Script
```python
inputs.exo_meeting_email_address = inputs.exo_meeting_email_address  if rule.properties.exo_meeting_email_address is None else rule.properties.exo_meeting_email_address
inputs.exo_meeting_start_time = inputs.exo_meeting_start_time if rule.properties.exo_meeting_start_time is None else rule.properties.exo_meeting_start_time
inputs.exo_meeting_end_time = inputs.exo_meeting_end_time if rule.properties.exo_meeting_end_time is None else rule.properties.exo_meeting_end_time
inputs.exo_meeting_subject = inputs.exo_meeting_subject if rule.properties.exo_meeting_subject is None else rule.properties.exo_meeting_subject
inputs.exo_meeting_body = inputs.exo_meeting_body if rule.properties.exo_meeting_body.content is None else rule.properties.exo_meeting_body.content
inputs.exo_meeting_required_attendees = inputs.exo_meeting_required_attendees if rule.properties.exo_meeting_required_attendees is None else rule.properties.exo_meeting_required_attendees
inputs.exo_meeting_optional_attendees = inputs.exo_meeting_optional_attendees if rule.properties.exo_meeting_optional_attendees is None else rule.properties.exo_meeting_optional_attendees
inputs.exo_meeting_location = inputs.exo_meeting_location if rule.properties.exo_meeting_location is None else rule.properties.exo_meeting_location
```

### Post-Processing Script
```python
if results.success:
  noteText = u"Exchange Online created meeting\n   From: {0}\n{1}".format(results.inputs["exo_meeting_email_address"],results.pretty_string)
else:
  noteText = u"Exchange Online meeting was NOT created\n   From: {0}\n{1}".format(results.inputs["exo_meeting_email_address"], results.pretty_string)

incident.addNote(noteText)
```

---

