from django.apps import apps
from django.db.models import F, Sum
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault, SerializerMethodField
from horologium.models import Timer, Duration, Countdown, Note


def get_db_name(obj):
    db_name = 'default'
    if obj._state.db is not None:
        db_name = obj._state.db
    return settings.DATABASES[db_name]['ENGINE'].split('.')[-1]


class BaseModelSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(ModelSerializer, self).__init__(*args, **kwargs)
        self.request = kwargs['context']['request']



class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class GroupSerializer(BaseModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class TimerSerializer(BaseModelSerializer):
    owner = PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUserDefault()
    )
    elapsed = SerializerMethodField(read_only=True)

    def get_elapsed(self, timer):
        if get_db_name(timer) != 'sqlite3':
            # Aggregating datetime fields doesn't work on sqlite, as the values are stored as text.
            return timer.durations.annotate(elapsed=F('end') - F('start')).aggregate(elapsed=Sum('elapsed'))

        total = 0
        for duration in timer.durations.all():
            end = duration.end
            if not end:
                end = timezone.now()
            total = total + (end - duration.start).total_seconds()
        return total

    def validate(self, data):
        if self.request.user.is_superuser:
            if not 'owner' in data:
                data['owner'] = self.request.user
        else:
            data['owner'] = self.request.user

        return data

    class Meta:
        model = Timer
        fields = ('id', 'name', 'description', 'owner', 'countdowns', 'durations', 'elapsed')
        unique_together = ('name', 'owner')


class DurationSerializer(BaseModelSerializer):
    def validate_timer(self, timer):
        if timer.owner != self.request.user and not self.request.user.is_superuser:
            raise ValidationError("Can not assign duration to other's timer.")
        return timer

    class Meta:
        model = Duration
        fields = ('id', 'start', 'end', 'timer')


class CountdownSerializer(BaseModelSerializer):
    def validate_timer(self, timer):
        if timer.owner != self.request.user and not self.request.user.is_superuser:
            raise ValidationError("Can not assign countdown to other's timer.")
        return timer

    class Meta:
        model = Countdown
        fields = ('id', 'count', 'timer', 'notice')


class NoteSerializer(BaseModelSerializer):
    writer = PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUserDefault()
    )

    def validate(self, data):
        if self.request.user.is_superuser:
            if not 'writer' in data:
                data['writer'] = self.request.user
        else:
            data['writer'] = self.request.user

        return data

    class Meta:
        model = Note
        fields = ('id', 'note', 'stamp', 'writer')
