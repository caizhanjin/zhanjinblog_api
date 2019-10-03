from rest_framework import views

import time

from .models import Image
from units.format_data import ReturnData
from units.permission import IsAdminUserOrReadOnly


class ImageAPIView(views.APIView):
    # permission_classes = (IsAdminUserOrReadOnly,)

    def post(self, request):
        image_data = request.FILES.get('image')
        if not image_data:
            return ReturnData(code=201, msg='没有接收到数据')

        image_data.name = str(int(time.time()))+image_data.name

        create_data = Image.objects.create(image_info=image_data)

        image_url = create_data.image_info.path
        if not image_url:
            return ReturnData(code=201, msg='图片上传失败')

        return ReturnData(data=image_url)
