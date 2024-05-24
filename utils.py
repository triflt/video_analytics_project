import json

def serializer(value):
    """
    Обмен данными происходит в байтах, поэтому мы должны
    сначала перевести наше значение JSON, а затем в байты
    """
    return json.dumps(value).encode()


def deserializer(serialized):
    """
    Десериализатор получаемых данных
    """
    return json.loads(serialized)