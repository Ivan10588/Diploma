from django.db import models

class Project(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Завершен'),
        ('archived', 'В архиве'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название проекта")
    image = models.ImageField(upload_to='projects/', verbose_name="Изображение проекта")
    description = models.TextField(verbose_name="Описание")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name="Статус"
    )
    technologies = models.TextField(blank=True, verbose_name="Технологии")
    completion_date = models.DateField(verbose_name="Дата завершения")
    project_url = models.URLField(blank=True, verbose_name="Ссылка на проект")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-completion_date']

    def __str__(self):
        return self.title
