from collections import namedtuple


no_request = 'NO_REQUEST'


Solar_Event = namedtuple(
    "Solar_Event",
    [
        "sol",
        "start_time",
        "end_time",
        "x_min",
        "x_max",
        "y_min",
        "y_max",
        "hgc_x",
        "hgc_y",
        "instrument",
        "event_id",
        "ssw_job_id"
    ],
    defaults = ( 'AIA', 'NO_ID', no_request)
)

Solar_Event.__doc__ = "Named tuple describing a single solar event"
