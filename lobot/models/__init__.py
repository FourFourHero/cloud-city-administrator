from basemodel import BaseModel

def model_encode(obj):
    enc = None
    try:
        enc = obj.__json__()
    except:
        logging.exception('Error encoding')
        enc = None

    if enc:
        return enc

    raise TypeError(repr(obj) + " is not JSON serializable")

def model_encode_verbose(obj):
    enc = None
    try:
        enc = obj.__json_verbose__()
    except Exception, e:
        logging.exception('Error encoding verbose')
        enc = None

    if enc:
        return enc

    raise TypeError(repr(obj) + " is not JSON serializable")
