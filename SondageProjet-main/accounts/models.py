from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Participant(models.Model):
    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"

    def __str__(self):
        return f"Participant #{self.pk}"

    def get_type(self):
        if hasattr(self, 'utilisateur'):
            return 'utilisateur'
        if hasattr(self, 'anonyme'):
            return 'anonyme'
        return 'inconnu'


class Utilisateur(AbstractUser):
    """
    On supprime l'héritage de Participant ici car AbstractUser + Participant
    cause des conflits de clés avec utf8mb4 dans MySQL.
    """
    ROLE_CHOICES = [
        ('createur', 'Créateur de sondages'),
        ('participant', 'Participant'),
        ('les_deux', 'Créateur et Participant'),
    ]

    email = models.EmailField(max_length=191, unique=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='les_deux')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def est_createur(self):
        return self.role in ['createur', 'les_deux']

    def est_participant(self):
        return self.role in ['participant', 'les_deux']

    def modifier_profil(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Anonyme(Participant):
    adresse_ip = models.GenericIPAddressField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date_premiere_reponse = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Participant Anonyme"
        verbose_name_plural = "Participants Anonymes"

    def identifier(self):
        return f"Anonyme-{str(self.token)[:8]}"

    def __str__(self):
        return self.identifier()