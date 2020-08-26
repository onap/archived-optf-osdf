from apps.nxi_termination.optimizers.response_processor import get_nxi_termination_response
from osdf.adapters.aai.fetch_aai_data import AAIException
from osdf.adapters.aai.fetch_aai_data import get_aai_data


def process_nxi_termination_opt(request_json, osdf_config):

    """Process the nxi Termination request from API layer

       :param request_json: api request
       :param osdf_config: configuration specific to OSDF app
       :return: response as a success,failure
    """

    type = request_json["type"]
    request_info = request_json.get("requestInfo", {})
    addtnl_args = request_info.get("addtnlArgs", {})
    if type == "NSI":
        arg_val = addtnl_args.get("serviceProfileId", "")
        return check_nxi_termination(request_json, osdf_config, addtnl_args, arg_val,
                                     get_service_profiles, get_service_profile_id)

    else:
        arg_val = addtnl_args.get("serviceInstanceId", "")
        return check_nxi_termination(request_json, osdf_config, addtnl_args, arg_val, get_relationshiplist, get_nsi_id)


def check_nxi_termination(request_json, osdf_config, addtnl_args, arg_val, get_response_object, get_response_id):
    request_info = request_json.get("requestInfo", {})

    try:
        response_object = get_response_object(request_json, osdf_config)
        if addtnl_args and arg_val and len(response_object) == 1:
            response_id = get_response_id(response_object)
            if arg_val == response_id:
                return set_success_response(request_info)

            else:
                reason = "{} is not available in AAI".format(arg_val)
                return set_failure_response(reason, request_info)

        elif len(response_object) == 0:
            return set_success_response(request_info)

        else:
            reason = "Associated to more than one"
            return set_failure_response(reason, request_info)

    except AAIException as e:
        return e

    except Exception as e:
        return "{} Exception Occurred while processing".format(e)


def get_service_profiles(request_json, osdf_config):
    try:
        json_response = get_aai_data(request_json, osdf_config)
        service_profiles = json_response.get("service-profiles", {})
        service_profile = service_profiles.get("service-profile", [])
        return service_profile
    except AAIException as e:
        raise AAIException(e)


def get_relationshiplist(request_json, osdf_config):
    try:
        json_response = get_aai_data(request_json, osdf_config)
        rel_list = json_response.get("relationship-list", {})
        relationship = rel_list.get("relationship", [])
        return relationship
    except AAIException as e:
        raise AAIException(e)


def get_service_profile_id(service_profile):
    profile_obj = service_profile[0]
    return profile_obj.get("profile-id", "")


def get_nsi_id(relationship):
    rel_obj = relationship[0]
    rel_data = rel_obj.get("relationship-data", [])
    for data in rel_data:
        if data["relationship-key"] == "service-instance.service-instance-id":
            return data["relationship-value"]


def set_success_response(request_info):
    res = dict()
    res["requestStatus"] = "success"
    res["terminateResponse"] = "True"
    res["reason"] = ""
    finalresponse = get_nxi_termination_response(request_info, res)
    return finalresponse


def set_failure_response(reason, request_info,):
    res = dict()
    res["requestStatus"] = "success"
    res["terminateResponse"] = "False"
    res["reason"] = reason
    finalresponse = get_nxi_termination_response(request_info, res)
    return finalresponse
