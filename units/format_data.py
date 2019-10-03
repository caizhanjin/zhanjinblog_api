from rest_framework import status
from rest_framework.response import Response


class ReturnData():
    """返回数据格式化"""
    def __new__(cls, code=200, msg="成功", data='', status=status.HTTP_200_OK, headers=None):
        data_info = {
            "code": code,
            "msg": msg,
            "data": data,
        }
        return Response(data=data_info, status=status, headers=headers)


class PageInfo():
    """列表数据格式化"""
    def __new__(cls, total=10, page_size=10, current_index=1):
        divide = int(total)/int(page_size)

        page_info = {
            'total': total,
            'page_size': page_size,
            'page_count': int(divide if int(divide) == divide else int(divide)+1),
            'current_index': current_index,
        }

        slice_begin = (current_index-1)*page_size
        slice_end = current_index*page_size

        return page_info, (slice_begin, slice_end)


