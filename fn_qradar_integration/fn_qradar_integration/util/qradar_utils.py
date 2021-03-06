# -*- coding: utf-8 -*-
#
# (c) Copyright IBM Corp. 2018. All Rights Reserved.
#
#   Util classes for qradar
#

import fn_qradar_integration.util.qradar_constants as qradar_constants
import base64
import logging
import six
from fn_qradar_integration.util.SearchWaitCommand import SearchWaitCommand, SearchFailure, SearchJobFailure
import fn_qradar_integration.util.function_utils as function_utils
from resilient_lib import RequestsCommon

from fn_qradar_integration.util.exceptions.custom_exceptions import RequestError, DeleteError
from ..lib.reference_data.ReferenceTableFacade import ReferenceTableFacade
# handle python2 and 3
try:
    from urllib import quote as quote_func  # Python 2.X
except ImportError:
    from urllib.parse import quote as quote_func  # Python 3+

LOG = logging.getLogger(__name__)
FORWARD_SLASH = b'%2F'


def quote(input_v, safe=None):
    """
    To make sure that integration on Python 2 works with unicode we will wrap quote
    to always pass bytes to it.
    """
    if not isinstance(input_v, six.binary_type):
        input_v = input_v.encode('utf-8')

    input_v = input_v.replace(b'/', FORWARD_SLASH)
    # No need to re-define the default for safe
    if safe:
        return quote_func(input_v, safe)
    return quote_func(input_v)


class AuthInfo(object):
    # Singleton
    __instance = None

    def __init__(self):
        self.headers = {}
        self.qradar_auth = None
        self.qradar_token = None
        self.api_url = None
        self.cafile = True
        self.rc = None
        pass

    @staticmethod
    def get_authInfo():
        if AuthInfo.__instance is None:
            AuthInfo.__instance = AuthInfo()
        return AuthInfo.__instance

    def create(self, host, username=None, password=None, token=None, cafile=None,
               opts=None, function_opts=None):
        """
        Create headers used for REST Api calls
        :param host: qradar host
        :param username: qradar user login
        :param password: qradar password
        :param token: Use token or username/password to auth
        :param cafile:
        :param opts: app.config options
        :param function_opts: function parameters from app.config
        :return:
        """
        self.headers = {'Accept': 'application/json'}
        if username and password:
            self.qradar_auth = base64.b64encode(
                (username + ':' + password).encode('ascii'))
            self.headers['Authorization'] = b"Basic " + self.qradar_auth
        elif token:
            self.qradar_token = token
            self.headers["SEC"] = self.qradar_token
        if host.startswith("http"):
            self.api_url = "{}/api/".format(host)
        else:
            self.api_url = "https://{}/api/".format(host)
        self.cafile = cafile

        self.rc = RequestsCommon(opts, function_opts)

    def make_call(self, method, url, headers=None, data=None):
        my_headers = headers if headers else self.headers

        def make_call_callback(response):
            # 404 is not found, such as reference not found or item not found in reference set
            if response.status_code in (404,):
                return response
            else:
                response.raise_for_status()
                return response

        return self.rc.execute_call_v2(method, url, data=data, headers=my_headers, verify=self.cafile, callback=make_call_callback)


class ArielSearch(SearchWaitCommand):
    """
    Subclass of SearchWaitCommand.
    Overrides/implements get_search_id, check_status, get_search_result for QRadar
    """

    def __init__(self, timeout=600, poll=5):
        self.range_start = 0
        self.range_end = 50
        self.query_all = False
        super(ArielSearch, self).__init__(timeout, poll)

    def set_range_start(self, start):
        """
        Set range start for ariel search
        :param start: int for range start
        :return:
        """
        self.range_start = start

    def set_range_end(self, end):
        """
        Set range end for ariel search
        :param end: int for range end
        :return:
        """
        self.range_end = end

    def set_timeout(self, timeout):
        """
        Set timeout
        :param timeout:
        :return:
        """
        self.search_timeout = timeout

    def set_query_all(self, query_all):
        """
        Set bool to determine if range header is necessary
        :param query_all:
        :return:
        """
        self.query_all = query_all

    def get_search_id(self, query):
        """
        Get the search if associated with the search using query
        :param query: input query string
        :return: search_id returned from QRadar
        """
        auth_info = AuthInfo.get_authInfo()
        url = auth_info.api_url + qradar_constants.ARIEL_SEARCHES
        utf8 = query.encode("utf-8")
        data = {"query_expression": utf8}

        search_id = ""
        try:
            response = auth_info.make_call("POST", url, data=data)

            json = response.json()
            if "search_id" in json:
                search_id = json["search_id"]
        except Exception as e:
            LOG.error(str(e))
            raise SearchJobFailure(query)

        return search_id

    def get_search_result(self, search_id):
        """
        Get search result associated with search_id
        :param search_id:
        :return: dict with events
        """
        auth_info = AuthInfo.get_authInfo()
        url = auth_info.api_url + \
            qradar_constants.ARIEL_SEARCHES_RESULT.format(search_id)

        headers = auth_info.headers.copy()
        # if the # of returned items is big, this call will take a long time!
        # Need to use Range to limit the # if query_all is False.
        # If query_all is True, the Range will not be used and all the results will be returned from the query.
        if not self.query_all:
            headers[b"Range"] = "items={}-{}".format(
                str(self.range_start), str(self.range_end))

        response = None
        try:
            response = auth_info.make_call("GET", url, headers=headers)
        except Exception as e:
            LOG.error(str(e))
            raise SearchFailure(search_id, None)

        ret = {}
        if response.status_code == 200:
            events = response.json()["events"]
            events = function_utils.fix_dict_value(events)
            ret = {"events": events}

        return ret

    def check_status(self, search_id):
        """
        Check the search status associated with search_id
        :param search_id:
        :return:
        """
        auth_info = AuthInfo.get_authInfo()
        url = "{}{}/{}".format(auth_info.api_url,
                               qradar_constants.ARIEL_SEARCHES, search_id)
        status = SearchWaitCommand.SEARCH_STATUS_ERROR_STOP
        try:
            response = auth_info.make_call("GET", url)

            json_dict = response.json()
            if "status" in json_dict:
                if json_dict["status"] == qradar_constants.SEARCH_STATUS_COMPLETED:
                    status = SearchWaitCommand.SEARCH_STATUS_COMPLETED
                elif json_dict["status"] == qradar_constants.SEARCH_STATUS_WAIT \
                    or json_dict["status"] == qradar_constants.SEARCH_STATUS_SORTING \
                        or json_dict["status"] == qradar_constants.SEARCH_STATUS_EXECUTE:
                    status = SearchWaitCommand.SEARCH_STATUS_WAITING

        except Exception as e:
            LOG.error(str(e))
            raise SearchFailure(search_id, status)

        return status



class QRadarClient(object):

    # QRadarClient has-a ReferenceTableFacade
    reference_tables = ReferenceTableFacade()
    auth_info = AuthInfo.get_authInfo()

    def __init__(self, host, username=None, password=None, token=None, cafile=None,
                 opts=None, function_opts=None):
        """
        Init
        :param host:  QRadar host
        :param username: QRadar user name
        :param password: QRadar password
        :param token: QRadar token
        :param cafile: verify cert or not
        :param opts: app.config options dictionary
        :param function_opts: function parameters from app.config
        """
        auth_info = AuthInfo.get_authInfo()
        auth_info.create(host, username, password, token,
                         cafile, opts, function_opts)

    def check_openssl(self):
        """
        Do we need to verify openssl version?
        :return:
        """

    def get_versions(self):
        """
        Util function used to test connectivity to QRadar
        :return:
        """
        auth_info = AuthInfo.get_authInfo()

        url = auth_info.api_url + qradar_constants.HELP_VERSIONS
        response = auth_info.make_call("GET", url)

        return response

    def ariel_search(self, query, query_all, range_start=None, range_end=None, timeout=None):
        """
        Perform an Ariel search
        :param query_all: bool used to decide if Range header is included in query
        :param query: query string
        :param range_start:
        :param range_end:
        :param timeout: timeout for search
        :return: dict with events
        """
        ariel_search = ArielSearch()
        if range_start is not None:
            ariel_search.set_range_start(range_start)

        if range_end is not None:
            ariel_search.set_range_end(range_end)

        if timeout is not None:
            ariel_search.set_timeout(timeout)

        ariel_search.set_query_all(query_all)

        response = ariel_search.perform_search(query)
        return response

    def verify_connect(self):
        """
        QRadar does not support session key. check version to verify
        Sample data
        [{"id":1,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"0.1"},
        {"id":2,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"0.2"},
        {"id":3,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"1.0"},
        {"id":4,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"2.0"},
        {"id":5,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"3.0"},
        {"id":6,"deprecated":false,"root_resource_ids":[],"removed":true,"version":"3.1"},
        {"id":7,"deprecated":true,"root_resource_ids":[1,7,14,16,18,28,44,51],"removed":false,"version":"4.0"},
        {"id":8,"deprecated":true,"root_resource_ids":[62,70,76,83,85,99,102,104,114,130,137,148],"removed":false,"version":"5.0"},
        {"id":9,"deprecated":true,"root_resource_ids":[157,165,171,178,180,194,199,201,211,227,234,245],"removed":false,"version":"5.1"},
        {"id":10,"deprecated":false,"root_resource_ids":[254,262,268,275,277,291,296,303,311,327,334,347],"removed":false,"version":"6.0"},
        {"id":11,"deprecated":false,"root_resource_ids":[356,390,408,417,419,471,480,491,496,503,514,526,572,579,602,607],"removed":false,"version":"7.0"}]
        """
        resp = self.get_versions()

        connected = False
        if resp.status_code == 200 and len(resp.json()) > 0:
            if "version" in resp.json()[0]:
                connected = True

        return connected

    @staticmethod
    def get_all_ref_set():
        """
        Get a list of all the reference sets.
        :return: list of reference set names
        """
        auth_info = AuthInfo.get_authInfo()
        url = u"{}{}".format(
            auth_info.api_url, qradar_constants.REFERENCE_SET_URL)
        ret = []
        try:
            response = auth_info.make_call("GET", url)
            #
            # Sample return:
            """
            [
                {
                    "timeout_type": "FIRST_SEEN",
                    "number_of_elements": 0,
                    "creation_time": 1516812810600,
                    "name": "Watson Advisor: File Action Blocked",
                    "element_type": "ALNIC"
                },
                ...
            ]
            """
            #
            ret = response.json()
        except Exception as e:
            LOG.error(str(e))
            raise RequestError(
                url, "get_all_ref_set call failed with exception {}".format(str(e)))

        return ret

    @staticmethod
    def find_all_ref_set_contains(value):
        """

        :param value:
        :param type:
        :return:
        """
        ref_sets = QRadarClient.get_all_ref_set()
        LOG.debug(u"All reference sets: {}".format(ref_sets))

        ret = []
        for r_set in ref_sets:
            LOG.info(u"Looking for {} in reference set {}".format(
                value, r_set["name"]))
            element = QRadarClient.search_ref_set(r_set["name"], value)
            if element["found"] == "True":
                ret.append(element["content"])

        return ret

    @staticmethod
    def search_ref_set(ref_set, filter=None):
        """
        Search a reference set using the filter
        :param ref_set: Reference set name
        :param filter:
        :return:
        """
        auth_info = AuthInfo.get_authInfo()

        ref_set_link = quote(ref_set, '')

        url = u"{}{}/{}".format(auth_info.api_url,
                                qradar_constants.REFERENCE_SET_URL, ref_set_link)

        ret = None
        try:
            if filter:
                if not isinstance(filter, six.binary_type):
                    filter = filter.encode('utf-8')
                parameter = quote('?value="{}"'.format(filter))
                url = url + parameter

            response = auth_info.make_call("GET", url)

            # Sample return
            # {"creation_time":1523020929069,"timeout_type":"FIRST_SEEN","number_of_elements":2,
            # "data":[{"last_seen":1523020984874,"first_seen":1523020984874,"source":"admin","value":"8.8.8.8"}],
            # "name":"Sample Suspect IPs","element_type":"IP"}
            found = "False"
            ret_data = response.json().get("data", [])

            # Check if there are elements in the reference set
            if len(ret_data) > 0 and response.status_code == 200:
                # Use dictionary comprehension on ret_data to determine if `filter` is assigned to the "value" in
                # any of the dictionaries items in the ret_data list
                # `element_found` will be None if the `filter` is not found in the data
                element_found = next(
                    (item for item in ret_data if item["value"].encode('utf-8') == filter), None)
                if element_found:
                    found = "True"

            ret = {"status_code": response.status_code,
                   "found": found,
                   "content": response.json()}

        except Exception as e:
            LOG.error(str(e))
            raise RequestError(
                url, "search_ref_set call failed with exception {}".format(str(e)))

        return ret

    @staticmethod
    def add_ref_element(ref_set, value):
        """
        Add the value to the given ref_set
        :param ref_set: Name of reference set.
        :param value:
        :return:
        """
        auth_info = AuthInfo.get_authInfo()
        ref_set_link = quote(ref_set, '')
        url = "{}{}/{}".format(auth_info.api_url,
                               qradar_constants.REFERENCE_SET_URL, ref_set_link)

        ret = None
        try:
            data = {"value": value}
            response = auth_info.make_call("POST", url, data=data)

            ret = {"status_code": response.status_code,
                   "content": response.json()}

        except Exception as e:
            LOG.error(str(e))
            raise RequestError(
                url, "add_ref_element call failed with exception {}".format(str(e)))

        return ret

    @staticmethod
    def delete_ref_element(ref_set, value, reference_endpoint=qradar_constants.REFERENCE_SET_URL):
        """
        Delete value from the given ref_set
        :param ref_set: Name of existing reference set
        :param value:
        :return:
        """
        auth_info = AuthInfo.get_authInfo()
        ref_set_link = quote(ref_set, '')
        value = quote(value, '')
        url = u"{}{}/{}/{}".format(auth_info.api_url, reference_endpoint,
                                   ref_set_link, value)

        ret = {}
        try:
            response = auth_info.make_call("DELETE", url)

            ret = {"status_code": response.status_code,
                   "content": response.json()}

        except Exception as e:
            LOG.error(str(e))
            raise DeleteError(
                url, "delete_ref_element failed with exception {}".format(str(e)))

        return ret

    @classmethod
    def get_ref_table_element(cls, ref_table, reference_endpoint=qradar_constants.REFERENCE_TABLE_URL):
        """
        Get value from the given ref_table
        :param ref_table: Name of reference table.
        :param value:
        :return:
        """
        return cls.reference_tables.get_one_reference_table(AuthInfo.get_authInfo(), ref_table)

    @classmethod
    def update_ref_table_element(cls, ref_table, inner_key, outer_key, value, reference_endpoint=qradar_constants.REFERENCE_TABLE_URL):
        """
        Delete value from the given ref_table
        :param ref_table: Name of reference table.
        :param value:
        :return:
        """
        return cls.reference_tables.update_ref_element(AuthInfo.get_authInfo(), ref_table, inner_key, outer_key, value)

    @classmethod
    def delete_ref_table_element(cls, ref_table, inner_key, outer_key, value, reference_endpoint=qradar_constants.REFERENCE_TABLE_URL):
        """
        Delete value from the given ref_table
        :param ref_table: Name of reference table.
        :param value:
        :return:
        """
        return cls.reference_tables.delete_ref_element(AuthInfo.get_authInfo(), ref_table, inner_key, outer_key, value)

    

    def get_all_ref_tables(self):
        return self.reference_tables.get_all_reference_tables(AuthInfo.get_authInfo())

    @classmethod
    def add_ref_table_element(cls, ref_table, inner_key, outer_key, value):
        """
        Add the value to the given ref_table
        :param ref_table: Name of reference table.
        :param value:
        :return:
        """
        return cls.reference_tables.add_ref_element(AuthInfo.get_authInfo(), ref_table, inner_key, outer_key, value)
        
