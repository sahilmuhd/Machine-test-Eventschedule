from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# -----------------------------
# SPEAKER MODEL
# -----------------------------
class Speaker(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# -----------------------------
# EVENT MODEL
# -----------------------------
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.title} - {self.date}"
    
class Meta:
    unique_together = ('event', 'title', 'start_time')


# -----------------------------
# SESSION MODEL
# -----------------------------
class Session(models.Model):
    title = models.CharField(max_length=200)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        # Skip if any required fields are missing
        if not all([self.event, self.speaker, self.start_time, self.end_time]):
            return

        # 1. Check for overlapping sessions in same event
        overlapping = Session.objects.filter(
            event=self.event,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("This session overlaps with another session in the same event.")

        # 2. Check for speaker conflict
        conflict = Session.objects.filter(
            speaker=self.speaker,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if conflict.exists():
            raise ValidationError("This speaker is already booked in another session at this time.")

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time})"
