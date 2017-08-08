from django.db.models.fields.files import ImageField, ImageFieldFile

from config import settings

__all__ = (
    'CustomImageFieldFile',
    'CustomImageField',
)


class CustomImageFieldFile(ImageFieldFile):
    @property
    def url(self):
        try:
            return super().url
        except ValueError:
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(self.fields.static_image_path.split("?")[0])


class CustomImageField(ImageField):
    attr_class = CustomImageFieldFile

    def __init__(self, *args, **kwargs):
        self.static_dir = kwargs.pop(
            'static_image_path',
            'member/base_profile.png'
        )
        super().__init__(*args, **kwargs)