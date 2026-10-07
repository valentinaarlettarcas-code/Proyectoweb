from rest_framework import serializers
from .models import Usuario


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        email = value.lower().strip()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo electrónico."
            )

        return email

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data['email']

        usuario = Usuario(
            username=email,
            rol=Usuario.Rol.CLIENTE,
            estado=Usuario.Estado.ACTIVO,
            **validated_data
        )

        usuario.set_password(password)
        usuario.save()

        return usuario

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email'].lower().strip()
        password = data['password']

        try:
            usuario = Usuario.objects.get(email__iexact=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Credenciales incorrectas.")

        if not usuario.check_password(password):
            raise serializers.ValidationError("Credenciales incorrectas.")

        if usuario.estado != Usuario.Estado.ACTIVO:
            raise serializers.ValidationError(
                "La cuenta no está activa."
            )

        data['usuario'] = usuario
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'rol',
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'rol',
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
        ]

    def validate_email(self, value):
        email = value.lower().strip()

        if Usuario.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo."
            )

        return email

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Mantenemos username sincronizado con el email.
        instance.username = instance.email
        instance.save(update_fields=['username'])

        return instance