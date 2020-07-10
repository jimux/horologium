from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
from sanitizer.models import SanitizedCharField


alphanumerics = RegexValidator(r'^[A-Za-z0-9][\.a-zA-Z0-9_@\-]*$', 'Alphanumerics only.')
minlength = MinLengthValidator(1, message='Field must not be empty')


class Timer(models.Model):
    """
    Tracks a sequence of durations.
    """
    name = SanitizedCharField(max_length=64, blank=True)
    description = SanitizedCharField(max_length=4096, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def start(self):
        if self.durations.count() and self.durations.filter(end__isnull=True).exists():
            return
            #raise ValueError("Can not start a timer that is already started.")

        duration = Duration(start=timezone.now(), timer=self)
        duration.save()

    def stop(self):
        active_duration = self.durations.get(end__isnull=True)
        if not active_duration:
            return
            #raise ValueError("Can not stop a timer that is not started.")

        active_duration.end = timezone.now()
        active_duration.save()

    def mark(self):
        active_duration = self.durations.get(end__isnull=True)
        if not active_duration:
            self.start()
            return

        active_duration.end = timezone.now()
        active_duration.save()

        new_duration = Duration(start=active_duration.end, timer=self)
        new_duration.save()



class Duration(models.Model):
    """
    Tracks a simple duration of time.
    """
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    timer = models.ForeignKey('Timer', related_name='durations', on_delete=models.CASCADE)

    def __str__(self):
        return "From %s to %s." % (str(self.start), str(self.end))


class Countdown(models.Model):
    """
    Count of seconds toward a goal.

    A timer can have multiple countdowns. One at 60 and another 120 will go off at 1 minute and 2 minutes respectively.
    """
    count = models.IntegerField(blank=True, null=True)
    timer = models.ForeignKey('Timer', related_name='countdowns', on_delete=models.CASCADE)
    notice = SanitizedCharField(max_length=1024, blank=True)

    class Meta:
        unique_together = ('count', 'timer')


class Note(models.Model):
    note = SanitizedCharField(max_length=4096, validators=[minlength])
    stamp = models.DateTimeField(auto_now_add=True)
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
