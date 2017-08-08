from django.db.models.fields.files import ImageField, ImageFieldFile, FieldFile

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
            return staticfiles_storage.url(self.field.static_image_path)


class CustomImageField(ImageField):
    attr_class = CustomImageFieldFile

    def __init__(self, *args, **kwargs):
        self.static_image_path = kwargs.pop(
            'default_static_image',
            'member/base_profile.png'
        )
        super().__init__(*args, **kwargs)