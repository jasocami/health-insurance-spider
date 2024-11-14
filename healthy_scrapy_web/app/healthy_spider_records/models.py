from django.db import models
from django.utils import timezone


class QuironRecord(models.Model):
    """
    Record for each item scraped
    """
    type_product_name = models.CharField(max_length=128, blank=True, null=True)
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=128, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return '{}: {} - {} - {} - {}'.format(self.type_product_name, self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class SaludonnetRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=128, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    group = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    health_registration = models.CharField(max_length=256, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class ClinicPointRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class SmartSalusRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class IglobalmedRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_middle = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.city)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class OperarmeRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.city)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class MiDiagnosticoRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.CharField(max_length=128, blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.CharField(max_length=256, blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class BonomedicoRecord(models.Model):
    """
    Record for each item scraped
    """
    product_name = models.TextField(blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.TextField(blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    health_registration = models.CharField(max_length=60, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)


class PortalsaludSanitasRecord(models.Model):
    """
    Record for each item scraped
    """

    GENDER_FEMALE = 'F'
    GENDER_MALE = 'M'
    GENDER_CHOICES = (
        (GENDER_FEMALE, 'Mujer'),
        (GENDER_MALE, 'Hombre')
    )

    product_name = models.TextField(blank=True, null=True)
    speciality_name = models.CharField(max_length=256, blank=True, null=True)
    pvp = models.CharField(max_length=64, blank=True, null=True)
    pvp_full = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    center = models.TextField(blank=True, null=True)
    province_name = models.CharField(max_length=64, blank=True, null=True)
    includes = models.TextField(blank=True, null=True)
    excludes = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, null=True)
    creation_timestamp = models.DateTimeField(default=timezone.now, blank=True)
    last_update_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.product_name, self.speciality_name, self.center, self.province_name)

    def save(self, *args, **kwargs):
        self.last_update_timestamp = timezone.now()
        super().save(*args, **kwargs)
