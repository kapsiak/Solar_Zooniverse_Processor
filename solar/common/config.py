class ConfMeta(type):
    def __getitem__(cls, key):
        return cls.__dict__[key]


class Map(dict):
    """
    The purpose of this class is to create an easy interface for accessing members of the configuration
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class Config(metaclass=ConfMeta):
    """
    This class holds the global configuration for the project.
    """

    # TODO: Allow this class to defined via a yaml/toml document #
    db_path = "test.db"
    db_save = "files"
    storage_path = Map(
        fits="fits/{event_id}/{server_file_name}",
        img="generated/{image_type}/{event.event_id}/{file_name}",
    )
    time_format = Map(hek="%Y-%m-%dT%H:%M:%S", fits="%Y-%m-%dT%H:%M:%S.%f")
    chatty = True
