# -*- coding: utf-8 -*-
"""Tests using pytest_resilient_circuits"""

from __future__ import print_function
import pytest
from resilient_circuits.util import get_config_data, get_function_definition
from resilient_circuits import SubmitTestFunction, FunctionResult

PACKAGE_NAME = "fn_urlscanio"
FUNCTION_NAME = "urlscanio"

# Read the default configuration-data section from the package
config_data = get_config_data(PACKAGE_NAME)

# Provide a simulation of the Resilient REST API (uncomment to connect to a real appliance)
resilient_mock = "pytest_resilient_circuits.BasicResilientMock"


def call_urlscanio_function(circuits, function_params, timeout=10):
    # Fire a message to the function
    evt = SubmitTestFunction("urlscanio", function_params)
    circuits.manager.fire(evt)
    event = circuits.watcher.wait("urlscanio_result", parent=evt, timeout=timeout)
    assert event
    assert isinstance(event.kwargs["result"], FunctionResult)
    pytest.wait_for(event, "complete", True)
    return event.kwargs["result"].value


class TestUrlscanio:
    """ Tests for the urlscanio function"""

    def test_function_definition(self):
        """ Test that the package provides customization_data that defines the function """
        func = get_function_definition(PACKAGE_NAME, FUNCTION_NAME)
        assert func is not None

    @pytest.mark.livetest
    @pytest.mark.parametrize("urlscanio_url, urlscan_incident_id, expected_results", [
        ("text", "text", {"value": "xyz"}),
        ("text", "text", {"value": "xyz"})
    ])
    def test_success(self, circuits_app, urlscanio_url, urlscan_incident_id, expected_results):
        """ Test calling with sample values for the parameters """
        function_params = { 
            "urlscanio_url": urlscanio_url,
            "urlscan_incident_id": urlscan_incident_id
        }
        results = call_urlscanio_function(circuits_app, function_params)
        assert(expected_results == results)
