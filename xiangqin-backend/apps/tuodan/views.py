from django.http import HttpResponse, Http404
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from . import models
from .serializers import AnLiSerializer, ImagesSerializer


# Create your views here.


class AnLi(APIView):
    def get(self, request):
        obj = models.XingFuAnLi.objects.all()
        # AssertionError: `HyperlinkedRelatedField` requires the request in the serializer context.
        # Add `context={'request': request}` when instantiating the serializer.
        context = {'request': request}
        serializer = AnLiSerializer(instance=obj, many=True, context=context)
        # print(serializer.data)
        data = {"code": 200, "data": serializer.data}
        return Response(data)

    def post(self, request):
        print(f"request.FILES:{request.FILES}")
        print(f"request.data:{request.data}")
        serializer = AnLiSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            print(f"serializer.validated_data:{serializer.validated_data}")
            serializer.save()
            return Response({"code": 200, "data": serializer.data, "msg": "插入成功!"})
        else:
            error_data = {"code": 402, "data": "", "msg": serializer.errors}

            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class ImagesDetailView(APIView):
    def get_object(self, pk):
        try:
            return models.Images.objects.get(pk=pk)
            # return models.Images.objects.filter(anliInfo_id__exact=pk)
        except models.Images.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        context = {"request": request}
        article = self.get_object(pk)
        print(f"查找到所有的Image对象{article}")
        serializer = ImagesSerializer(instance=article, context=context)
        return Response(serializer.data)
