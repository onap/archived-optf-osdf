import requests
from requests.auth import HTTPBasicAuth
from requests import RequestException


class AAIException(Exception):
    pass


def get_aai_data(request_json, osdf_config):

    """Get the response from AAI

       :param request_json: requestjson
       :param osdf_config: configuration specific to OSDF app
       :return:response body from AAI
    """
    aai_headers = {
        "X-TransactionId": "9999",
        "X-FromAppId": "OOF",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    nxi_id = request_json["NxIId"]
    config = osdf_config.deployment
    aai_url = config["aaiUrl"]
    aai_req_url = aai_url + config["aaiServiceInstanceUrl"] + nxi_id + "?depth=2"

    try:
        response = requests.get(aai_req_url, aai_headers, auth=HTTPBasicAuth("AAI", "AAI"), verify=False)
    except RequestException as e:
        raise AAIException("Request exception was encountered {}".format(e))

    if response.status_code == 200:
        return response.json()
    else:
        raise AAIException("Error response recieved from AAI for the request {}".format(aai_req_url))
