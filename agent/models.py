from django.db import models


class ResearchMaterial(models.Model):
    FILE_TYPES = (
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('pdf', 'Document'),
    )

    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_type = models.CharField(max_length=50, choices=FILE_TYPES)  # Increased length for flexibility

    # We keep your 'uploaded_at' and add 'updated_at' for senior dev tracking
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This stores the AI's analysis
    analysis_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.file_type.upper()}: {self.title or self.file.name}"