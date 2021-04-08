*** Settings ***
Library       copy
Library       json
Library       Collections
Library       OperatingSystem
Resource          ./resources/common-keywords.robot

Suite Teardown  Delete All Sessions

*** Variables ***
&{placement_auth} =    username=test   password=testpwd

*** Keywords ***

NxiTerminationRequest
    [Documentation]    Sends request to NxiTermination API
    [Arguments]  ${data}
    ${data_str}=     json.dumps    ${data}
    ${resp}=         Http Post        host=${osdf_host}   restUrl=/api/oof/terminate/nxi/v1     data=${data_str}   auth=${placement_auth}
    ${response_json}    json.loads    ${resp.content}
    Should Be Equal As Integers    ${resp.status_code}    200
    [Return]  ${response_json}

*** Test Cases ***

TerminationRequestGeneration
    [Documentation]  This test case will generate request json for different scenarios
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}termination_request.json
    ${nsi_termination_request}=       json.loads    ${data}
    Set Global Variable       ${nsi_termination_request}
    ${nssi_termination_request}=      copy.deepcopy  ${nsi_termination_request}
    Set To Dictionary         ${nssi_termination_request}     type=NSSI
    Set Global Variable       ${nssi_termination_request}
    ${nsi_termination_request_args}=      copy.deepcopy  ${nsi_termination_request}
    ${request_info}=          Set Variable      ${nsi_termination_request_args["requestInfo"]}
    ${addtnl_args}=           Create Dictionary  serviceProfileId=660ca85c-1a0f-4521-a559-65f23e794699
    Set To Dictionary         ${request_info}      addtnlArgs=${addtnl_args}
    Set To Dictionary         ${nsi_termination_request_args}      requestInfo=${request_info}
    Set Global Variable       ${nsi_termination_request_args}
    ${nssi_termination_request_args}=      copy.deepcopy  ${nssi_termination_request}
    ${request_info}=          Set Variable      ${nssi_termination_request_args["requestInfo"]}
    ${addtnl_args}=           Create Dictionary  serviceInstanceId=660ca85c-1a0f-4521-a559-65f23e794699
    Set To Dictionary         ${request_info}      addtnlArgs=${addtnl_args}
    Set To Dictionary         ${nssi_termination_request_args}      requestInfo=${request_info}
    Set Global Variable       ${nssi_termination_request_args}

NSITermination
    [Documentation]    It sends a NSI termination request with no additional arguments
    ${response_json}=   NxiTerminationRequest         ${nsi_termination_request}
    Should Be Equal     success    ${response_json['requestStatus']}
    Should Be True       ${response_json['terminateResponse']}

NSSITermination
    [Documentation]    It sends a NSSI termination request with no additional arguments
    ${response_json}=   NxiTerminationRequest         ${nssi_termination_request}
    Should Be Equal     success    ${response_json['requestStatus']}
    Should Be True       ${response_json['terminateResponse']}

NSITerminationWithAddtnlArgs
    [Documentation]  It sends a NSSI termination request with additional arguments
    ${response_json}=   NxiTerminationRequest         ${nsi_termination_request_args}
    Should Be Equal     success    ${response_json['requestStatus']}
    Should Be True       ${response_json['terminateResponse']}

NSSITerminationWithAddtnlArgs
    [Documentation]  It sends a NSSI termination request with additional arguments
    ${response_json}=   NxiTerminationRequest         ${nssi_termination_request_args}
    Should Be Equal     success    ${response_json['requestStatus']}
    Should Be True       ${response_json['terminateResponse']}
