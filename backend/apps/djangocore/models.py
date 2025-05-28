from django.db import models
from encrypted_model_fields.fields import EncryptedTextField

# Create your models here.
class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value =  EncryptedTextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"