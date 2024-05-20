from sqlalchemy_serializer import SerializerMixin


class CustomSerializerMixin(SerializerMixin):
    # date_format = "%s"  # Unixtimestamp (seconds)
    # datetime_format = "%Y %b %d %H:%M:%S.%f"
    # time_format = "%H:%M.%f"
    decimal_format = "{:0>10.3}"
