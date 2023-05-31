from .models import Reserve
from rest_framework import viewsets, permissions
from .serializers import ReserveSerializer

class ReserveViewSet(viewsets.ModelViewSet):
    queryset = Reserve.objects.all()
    permissions_classes = [permissions.AllowAny()]
    serializer_class = ReserveSerializer