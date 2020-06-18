from solar.service import Hek_Service, Cutout_Service
from solar.database import *
import peewee as pw

create_tables()

h = Hek_Service()
h.submit_request()
h.fetch_data()
for e in h.data:
    try:
        e.save()
    except pw.IntegrityError:
        pass

#c_list = [Cutout_Service._from_event(e) for e in Solar_Event.select()]
#for x in c_list:
#    print(x)
#    x.submit_request()
#    x.save_request()
#    x.fetch_data()
#    x.save_request()
#
#for x in c_list:
#    for f in x.data:
#        try:
#            f.save()
#        except pw.IntegrityError:
#            pass

Fits_File.update_table()
