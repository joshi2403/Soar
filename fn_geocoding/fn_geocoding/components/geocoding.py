# (c) Copyright IBM Corp. 2018. All Rights Reserved.
# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use
"""Function implementation"""

import logging
from resilient_circuits import ResilientComponent, function, handler, StatusMessage, FunctionResult, FunctionError
from resilient_lib import RequestsCommon, validate_fields


class FunctionComponent(ResilientComponent):
    """Component that implements Resilient function 'geocoding_get_address"""
    VALID_SOURCES = ('address', 'latlng')

    def __init__(self, opts):
        """constructor provides access to the configuration options"""
        super(FunctionComponent, self).__init__(opts)
        self.opts = opts
        self.options = opts.get("fn_geocoding", {})

    @handler("reload")
    def _reload(self, event, opts):
        """Configuration options have changed, save new values"""
        self.opts = opts
        self.options = opts.get("fn_geocoding", {})

    @function("geocoding")
    def _geocoding_get_function(self, event, *args, **kwargs):
        """Function: two function types implemented: address and latlng.
           For an address, return coordinate information.
           For coordinates, return an address.
           see: https://developers.google.com/maps/documentation/geocoding/start
        """
        try:
            # Get the function parameters:
            geocoding_source = self.get_select_param(kwargs.get("geocoding_source"))  # String
            geocoding_data = kwargs.get("geocoding_data")  # String

            log = logging.getLogger(__name__)
            log.info("geocoding_source: %s", geocoding_source)
            log.info("geocoding_data: %s", geocoding_data)

            # confirm app.config setup
            validate_fields(['url', 'api_key'], self.options)

            # choices are set in the workflow: lnglat or address
            if geocoding_source not in FunctionComponent.VALID_SOURCES:
                raise ValueError("geocoding_source must be one of these values: %s", FunctionComponent.VALID_SOURCES)

            if geocoding_source == "latlng":
                if len(geocoding_data.split(',')) != 2:
                    raise ValueError("geocoding_data must be comma separated numeric values such as 42.3656119,-71.0805841")
                # api can't handle spaces
                geocoding_data = geocoding_data.strip()

            yield StatusMessage("starting...")

            url = self.options['url']
            payload = {
                "key": self.options['api_key'],
                geocoding_source: geocoding_data
            }

            log.debug(payload)
            rc = RequestsCommon(self.opts, self.options)
            response = rc.execute_call_v2("get", url, params=payload)
            resp = response.json()

            results = {
                "response": resp,
                "status": True if resp.get('status', '') == "OK" else False
            }

            yield StatusMessage("done...")

            # Produce a FunctionResult with the results
            yield FunctionResult(results)
        except Exception:
            yield FunctionError()
