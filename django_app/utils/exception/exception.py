from rest_framework.views import exception_handler


# status code 삽입
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


# 커스텀 에러메세지 믹스인 정의
class SetCustomErrorMessagesMixin:
    def __init__(self, *args, **kwargs):
        super(SetCustomErrorMessagesMixin, self).__init__(*args, **kwargs)
        self.replace_validators_messages()

    # 필드명(key)과 오류메세지를 보여주는 메서드
    def replace_validators_messages(self):
        for field_name, validators_lookup in self.custom_error_messages_for_validators.items():
            for validator in self.fields[field_name].validators:
                if type(validator) in validators_lookup:
                    validator.message = validators_lookup[type(validator)]

    @property
    def custom_error_messages_for_validators(self):
        meta = getattr(self, 'Meta', None)
        return getattr(meta, 'custom_error_messages_for_validators', {})
