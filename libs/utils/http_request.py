import requests
from requests import request

from utils.log import logger


def get_token(request):
    return request.META.get('HTTP_AUTHORIZATION')


# def send_request(url, token, params=None):
#     try:
#         result = requests.get(url, headers={'Authorization': token}, params=params)
#         status_code = result.status_code
#         result = result.json()
#         if result.get('rescode') == '10000':
#             return True, result.get('data')
#         return False, None
#     except Exception as ex:
#         logger.error('{0} 调用失败:{1}'.format(url, ex))
#         return False, None


def send_request(url, token=None, method='get', params=None, data=None):
    try:
        result = request(method, url, headers={'Authorization': token}, params=params, data=data, verify=False)
        status_code = result.status_code
        result = result.json()
        print(data)
        print(result)
        if result.get('rescode') == '10000':
            return True, result.get('data')
        return False, result.get('msg')
    except Exception as ex:
        logger.error('{0} 调用失败:{1}'.format(url, ex))
        return False, '{0}'.format(ex)
