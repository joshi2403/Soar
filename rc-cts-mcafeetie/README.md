# McAfee TIE Threat Searcher

This Custom Threat Source uses the Python OpenDXL TIE Client to communicate with your TIE server, which is located at
[GitHub: opendxl-tie-client-python](https://github.com/opendxl/opendxl-tie-client-python).

## Prerequisites
* System must have an OpenSSL version used by Python that supports TLSv1.2 (Version 1.0.1 or greater)
* ePO-managed environments must have 4.0 (or newer) version of DXL ePO extension installed

## Installation
1. Unzip rc-cts-mcafee-x.x.x.tar.gz.zip
2. Install this package with `pip`.
3. Once installed, the DXL client must be provisioned. Click [here](https://opendxl.github.io/opendxl-client-python/pydoc/provisioningoverview.html) for more info on provisioning.

4. Use the following commands to register this custom threat service with Resilient and test it:
```
    sudo resutil threatserviceedit -name "McAfee TIE Searcher" -resturl http://localhost:9000/cts/mcafee_tie_searcher
    sudo resutil threatservicetest -name "McAfee TIE Searcher"
```

5. Run `resilient-circuits config -u` to install the app.config settings and then edit the `[mcafee]` section with your DXL client configuration file information.
6. Run with: `resilient-circuits run`