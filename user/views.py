from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

@api_view(['POST'])
def logout(request):
    # Obtener el token de autenticación del usuario autenticado
    auth_token = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[-1]

    # Buscar el token en la base de datos
    try:
        token = Token.objects.get(key=auth_token)
    except Token.DoesNotExist:
        return Response({'error': 'Token inválido.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Eliminar el token
    token.delete()

    return Response({'success': 'Cierre de sesión exitoso.'}, status=status.HTTP_200_OK)