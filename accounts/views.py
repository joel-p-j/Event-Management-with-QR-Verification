from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User registered successfully!"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        data={
            'username':user.username,
            'email':user.email,
            'role':user.role
        }
        return Response(data)
    def put(self,request):
        user=request.user
        user.email=request.data.get('email',user.email)
        user.save()
        return Response({'message':'Profile updated successfully!'})