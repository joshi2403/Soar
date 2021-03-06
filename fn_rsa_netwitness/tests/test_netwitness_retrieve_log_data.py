# -*- coding: utf-8 -*-
"""Tests using pytest_resilient_circuits"""

from __future__ import print_function
import pytest
from resilient_circuits.util import get_config_data, get_function_definition
from resilient_circuits import SubmitTestFunction, FunctionResult

PACKAGE_NAME = "fn_rsa_netwitness"
FUNCTION_NAME = "netwitness_retrieve_log_data"

# Read the default configuration-data section from the package
# config_data = get_config_data(PACKAGE_NAME)

# Provide a simulation of the Resilient REST API (uncomment to connect to a real appliance)
resilient_mock = "pytest_resilient_circuits.BasicResilientMock"


def call_netwitness_retrieve_log_data_function(circuits, function_params, timeout=10):
    # Fire a message to the function
    evt = SubmitTestFunction("netwitness_retrieve_log_data", function_params)
    circuits.manager.fire(evt)
    event = circuits.watcher.wait("netwitness_retrieve_log_data_result",\
        parent=evt, timeout=timeout)
    assert event
    assert isinstance(event.kwargs["result"], FunctionResult)
    pytest.wait_for(event, "complete", True)
    return event.kwargs["result"].value


class TestNetwitnessRetrieveLogData:
    """ Tests for the netwitness_retrieve_log_data function"""

    def test_function_definition(self):
        """ Test that the package provides customization_data that defines the function """
        func = get_function_definition(PACKAGE_NAME, FUNCTION_NAME)
        assert func is not None

    @pytest.mark.livetest
    @pytest.mark.parametrize("nw_start_time, nw_end_time, nw_data_format, expected_results", [
        (1545157725000, 1545158725000, 'logs_text', {"value": "xyz"})
    ])
    def test_success(self, circuits_app, nw_start_time, nw_end_time, nw_data_format,\
        expected_results):
        """ Test calling with sample values for the parameters """
        function_params = {
            "nw_start_time": nw_start_time,
            "nw_end_time": nw_end_time,
            "nw_data_format": nw_data_format
        }
        results = call_netwitness_retrieve_log_data_function(circuits_app, function_params)
        assert results["content"] is not None
