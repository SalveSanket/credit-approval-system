from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, RegisterResponseSerializer

@api_view(["POST"])
def register(request):
    ser = RegisterSerializer(data=request.data)
    if not ser.is_valid():
        return Response({"errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
    customer = ser.save()
    out = RegisterResponseSerializer(customer)
    return Response(out.data, status=status.HTTP_201_CREATED)