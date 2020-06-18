class ConfMeta(type):
    def __getitem__(cls, key):
        return cls.__dict__[key]


class Config(metaclass=ConfMeta):
    db_path = "test.db"
    db_save = "files"
    storage_path = dict(
            fits = "fits/{event_id}/{server_file_name}"
        , img = "generated/{image_type}/{sol_standard}/{file_name}"
            )
    time_format = dict(
    hek = "%Y-%m-%dT%H:%M:%S"
    fits = "%Y-%m-%dT%H:%M:%S.%f"
    )
    chatty = True
