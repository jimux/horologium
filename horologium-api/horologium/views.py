from django.contrib.auth.models import Group, User
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings
from horologium.models import Timer, Duration, Countdown, Note
from horologium.serializers import GroupSerializer, UserSerializer, TimerSerializer, DurationSerializer, \
    CountdownSerializer, NoteSerializer


class SignUpViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        ## TODO: Best practice to handle password?
        serializer.instance.set_password(request.data['password'])
        serializer.instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TimerViewSet(viewsets.ModelViewSet):
    serializer_class = TimerSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Timer.objects.all()
        return Timer.objects.filter(owner=user)

    @action(methods=['put'], detail=True)
    def start(self, request, pk=None, **kwargs):
        queryset = self.get_queryset()
        timer = get_object_or_404(queryset, pk=pk)
        timer.start()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def stop(self, request, pk=None, **kwargs):
        queryset = self.get_queryset()
        timer = get_object_or_404(queryset, pk=pk)
        timer.stop()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def mark(self, request, pk=None, **kwargs):
        queryset = self.get_queryset()
        timer = get_object_or_404(queryset, pk=pk)
        timer.mark()
        return Response(status=status.HTTP_200_OK)


class DurationViewSet(viewsets.ModelViewSet):
    serializer_class = DurationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Duration.objects.all()
        return Duration.objects.filter(timer__owner=user)


class CountdownViewSet(viewsets.ModelViewSet):
    serializer_class = CountdownSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Countdown.objects.all()
        return Countdown.objects.filter(timer__owner=user)


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Note.objects.all()
        return Note.objects.filter(writer=user)