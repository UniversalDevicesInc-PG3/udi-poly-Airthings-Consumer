
import os,socket,struct,json,re,hashlib

def myfloat(value, prec=4):
    """ round and return float """
    return round(float(value), prec)

# F = (C × 9/5) + 32
def CtoF(value):
    return (float(value) * 9/5) + 32

def id_to_address(address,slen=14):
    slen = slen * -1
    m = hashlib.md5()
    m.update(address.encode())
    return m.hexdigest()[slen:]

def str_d(value):
    # Only allow utf-8 characters
    #  https://stackoverflow.com/questions/26541968/delete-every-non-utf-8-symbols-froms-string
    return bytes(value, 'utf-8').decode('utf-8','ignore')
