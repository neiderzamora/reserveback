from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .utils import *
from .email import *

from .models import Reserve
from .serializers import ReserveSerializer
from datetime import datetime, time, timedelta

from django.core.mail import send_mail

class ReserveList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reserve = Reserve.objects.all()
        serializer = ReserveSerializer(reserve, many=True)
        return Response(serializer.data)

class ReservePost(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ReserveSerializer(data=request.data)
        if serializer.is_valid():
            # Validate reservation
            date = serializer.validated_data['date']
            hour = serializer.validated_data['hour']
            campus = serializer.validated_data['campus']
            num_person = serializer.validated_data['num_person']
            
            serializer.save()

            # Send email to customer
            name = serializer.validated_data['name']
            last_name = serializer.validated_data['last_name']
            email = serializer.validated_data['email']
            date = serializer.validated_data['date']
            hour = serializer.validated_data['hour']
            send_confirmation_email(name, last_name, email, date, hour)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReserveDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Reserve.objects.get(pk=pk)
        except Reserve.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        reserve = self.get_object(pk)
        serializer = ReserveSerializer(reserve)
        return Response(serializer.data)

    def put(self, request, pk):
        reserve = self.get_object(pk)
        serializer = ReserveSerializer(reserve, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reserve = self.get_object(pk)
        reserve.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)