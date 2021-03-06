<!--
    DO NOT MANUALLY EDIT THIS FILE
    THIS FILE IS AUTOMATICALLY GENERATED WITH resilient-circuits codegen
-->

# Example: ICDx Search for Events related to IP

## Function - ICDx: Find Events

### API Name
`icdx_find_events`

### Output Name
`None`

### Message Destination
`fn_icdx`

### Pre-Processing Script
```python
#######################################
### Define pre-processing functions ###
#######################################
payload = {
   "Query_Title": "Query ran against an artifact of Type IP",
   "id" : 1,
   "start"  : "-7d",
   "where"  : "",
   "limit"  : 3
   }
def dict_to_json_str(d):
  """Function that converts a dictionary into a JSON stringself.
     Supports basestring, bool and int.
     If the value is None, it sets it to False"""

  json_str = '"{ {0} }"'
  json_entry = '"{0}":{1}'
  json_entry_str = '"{0}":"{1}"'
  entries = [] 
  
  for entry in d:
    key = entry
    value = d[entry]
    
    """
    The where attribute of the search request only works on a certain number of 'indexed' attributes such as device_ip
    
    If you want to search against other attributes such as email_sender_ip, a SHA hash or a MAC address, you may need to use the Filter attribute
    The Query Language is very flexible and includes a number of operations you can try. Review the ICDx Search Guide for more information.
    """
    if key == "where":
      value = "device_ip = '"+artifact.value+"'"
      
    """
    if key == "filter":
      value = "<attribute_you_want_to_search>" = '"+artifact.value+"'"
    """
      
      
    if value is None:
      value = False
      
    
    if isinstance(value, basestring):
      entries.append(json_entry_str.format(key, value))
    
    elif isinstance(value, bool):
      value = 'true' if value == True else 'false'
      entries.append(json_entry.format(key, value))
    
    else:
      entries.append(json_entry.format(key, value))
  
  return '{' + ','.join(entries) + '}'
  
  
inputs.icdx_search_request = dict_to_json_str(payload)

```

### Post-Processing Script
```python
"""
Example of the return data for this workflow
results = {
            "success": True or False
            "result_set": [{
              Object containing ICDx event data
            }],
            "num_of_results": How many results returned (INT),
            "execution_time": The time the function was executed
          }

"""
noteText = u"""<br><b>Search Request executed on ICDx :</b>"""

noteText += u"""<br>Number of results found: <b>{0}</b>
               <br>Results are being inserted into the ICDX Event Datatable""".format(results.num_of_results)

if results.inputs["icdx_search_request"]["Query_Title"] != None:
  noteText += u"""<br><br>A Query_Title attribute was provided with the input payload. 
                <br>Query Title: <b>{0} </b>""".format(results.inputs["icdx_search_request"]["Query_Title"])
  # If the where clause isin't Nonetype or empty
  if results.inputs["icdx_search_request"]["where"] not in (None, ''):
    noteText += u"""<br> Where Condition: <b>{0} </b>""".format(results.inputs["icdx_search_request"]["where"]) 
  if results.inputs["icdx_search_request"]["filter"] not in (None, ''):
    noteText += u"""<br> Filter Condition: <b>{0} </b>""".format(results.inputs["icdx_search_request"]["filter"])
                
if results.num_of_results >= results.inputs["icdx_search_request"]["hard_limit"]:
  noteText += u"""<br><br>Query resulted in {0} matching events. ICDx Event Requests are batched with a configurable limit of {1}.
              <br> To access any results after the {1}th returned result, please review the app.config parameter `icdx_search_limit` and update where necessary. 
              <br> The Last UUID appears to be <b>{2}</b>""".format(results.inputs["icdx_search_request"]["limit"],results.inputs["icdx_search_request"]["hard_limit"], results.result_set[-1]["uuid"])

incident.addNote(helper.createRichText(noteText))
if results.result_set:
  for event in results.result_set:
    # Now have a handle on each event; Prepare DataTable
    row = incident.addRow("icdx_events")
    row["icdx_uuid"]  = event['uuid']
    row["icdx_severity_id"]  = event['severity_id']
    row["icdx_device_name"]  = event['device_name']
    row["icdx_device_ip"]  = event['device_ip']
    row["execution_time"] = results.execution_time
    row["artifact_type"] = artifact.type
    try:
      row["icdx_type"] = event['type']
    except:
      row["icdx_type"] = u"""No Type"""
    
```

---

