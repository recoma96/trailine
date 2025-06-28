from enum import Enum


class CustomEnumType(Enum):
    """
    Serializer ChoiceField 에서 사용하기 위한 Enum Type
    """
    @classmethod
    def choices(cls):
        return [(tag.value, tag.name.replace("_", " ").title()) for tag in cls]
