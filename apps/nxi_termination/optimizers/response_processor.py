def get_nxi_termination_response(request_info, response):

    """Get NXI termination response from final solution

       :param request_info: request info
       :param response: response to be send
       :return: NSI Termination response to send back as dictionary
    """
    return {'requestId': request_info['requestId'],
            'transactionId': request_info['transactionId'],
            'requestStatus': response["requestStatus"],
            'terminateResponse': response["terminateResponse"],
            'reason': response['reason']}
