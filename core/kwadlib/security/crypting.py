## Copyright (c) 2007-2024, Patrick Germain Placidoux
## All rights reserved.
##
## This file is part of KastMenu (Unixes Operating System's Menus Broadkasting).
##
## KastMenu is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## KastMenu is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with KastMenu.  If not, see <http://www.gnu.org/licenses/>.
##
## Home: http://www.kastmenu.org
## Contact: kastmenu@kastmenu.org


# 2023/02/27  | M001 | Crypt renamed: AE32SCrypt.

import base64
import random
random.seed()
import re
RE_AZ09 = re.compile('[A-Za-z_0-9-]+')
RE_09 = re.compile('[0-9]+')
RE_AZaz = re.compile('[A-Za-z]+')
RE_AZaz09DOTSLASH = re.compile('[A-Za-z_0-9-\.\/]*')
RE_AZazHYPHEN = re.compile('[A-Za-z_0-9-\.]+')
RE_URL = re.compile('[:/A-Za-z_0-9-\.\/]*')
# RE_KASTMENU = re.compile('[=:/A-Za-z_0-9-\.\/,§@#!\[\]\(\)£\+]*')
RE_KASTMENU = re.compile('[^$~\s%|&<>]*')
RE_AZaz09DOT = re.compile('[A-Za-z_0-9\.]*')
RE_MAIL = re.compile('[A-Za-z_0-9\.]+@[A-Za-z_0-9]+\.[A-Za-z_0-9]+')


from kwadlib.default import *

CRYPT_PREFIX = '{KCrypted}'
SSLCRYPT_PREFIX = '{KSSLCrypted}' # Crypt only small text like password (designed for signature).


P_CACHES={}

def genUid(lite=False):
    """
    Generats a Unique Id.
    """
    import time

    id = str(int(time.time() * 100))
    rand = random.randint(1, 100000)

    if lite: return "%05i" % rand
    return id + "%05i" % rand



def __sanitize(*args, fct_sanitize=None, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    selfMethod='sanitize_base'
    for v in args:
        if allowNone and v==None:continue
        if v==None:raise Exception('Class: %s, Method: %s: Value cannot be None !' % ('Main', selfMethod))
        fct_sanitize(str(v), do_hide=do_hide)

    for key, v in kws.items():
        if allowNone and v==None:continue
        if v==None:raise Exception('Class: %s, Method: %s: Value%s cannot be None !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, ' for Parameter: %s' % key))
        fct_sanitize(str(v), do_hide=do_hide, key=key, class_exit=class_exit, method_exit=method_exit)

def __sanitize_base(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    selfMethod='sanitize'
    if v == '': return None

    R = RE_AZ09
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_name(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    selfMethod='sanitize_name'
    if v=='':return None

    # First char must be a Letter:
    r1 = RE_AZaz.match(v[0])
    # Check the last:
    R = RE_AZ09
    r2 = RE_AZ09.match(v)
    if r1 == None or r2 == None or r2.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_int(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    selfMethod='sanitize_int'
    if v=='':return None

    # Check Num
    R = RE_09
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_path(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Path:
    """
    selfMethod='sanitize_path'
    if v == '': return None

    R = RE_AZaz09DOTSLASH
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))


def __sanitize_host(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    selfMethod='sanitize'
    if v=='':return None

    # First char must be a Letter:
    r1 = RE_AZaz.match(v[0])
    # Check the last:
    R = RE_AZazHYPHEN
    r2 = RE_AZazHYPHEN.match(v)
    if r1 == None or r2 == None or r2.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))


def __sanitize_ip(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Path:
    """
    selfMethod='sanitize_ip'
    if v == '': return None

    R = RE_AZaz09DOT
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_hostorip(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Path:
    """
    selfMethod = 'sanitize_hostorip'
    if v == '': return None

    R = RE_AZazHYPHEN
    r = R.match(v)
    if r == None or r.group() != v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))


def __sanitize_url(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Path:
    """
    selfMethod='sanitize_url'
    if v == '': return None

    R = RE_URL
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_mail(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Mail:
    """
    selfMethod='sanitize_mail'
    if v == '': return None

    # First char must be a Letter:
    r1 = RE_AZaz.match(v[0])
    r2 = RE_MAIL.match(v)
    r3 = None
    # First char of part2 must be a Letter:
    if v.find('@')>0:
        part2 = v.split('@')[-1]
        r3 = RE_AZaz.match(part2[0])

    if r1 == None or r2 == None or r3 == None or r2.group() != v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % RE_MAIL.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, RE_MAIL.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))

def __sanitize_kastmenu(v, do_hide=False, key=None, class_exit=None, method_exit=None):
    """
    Sanitize Check Path:
    """
    selfMethod='kastmenu'
    if v == '': return None

    R = RE_KASTMENU
    r = R.match(v)
    if r == None or r.group()!=v:
        if do_hide:message = 'Unsupported character in password ! Expected value is: %s.' % R.pattern
        else:message = 'Unsupported value: %s ! Expected value is: %s.' % (v, R.pattern)
        raise Exception('Class: %s, Method: %s: %s%s !' % (class_exit if class_exit else 'Main', method_exit if method_exit else selfMethod, message, (' for Parameter: %s' % key) if key else ''))



def sanitize(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_base, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1:return args[0]

def sanitize_name(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_name, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_int(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_int, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_path(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_path, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_host(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_host, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_ip(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_ip, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_hostorip(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_hostorip, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_url(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_url, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_mail(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_mail, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]

def sanitize_kastmenu(*args, do_hide=False, allowNone=False, class_exit=None, method_exit=None, **kws):
    __sanitize(*args, fct_sanitize=__sanitize_kastmenu, do_hide=do_hide, allowNone=allowNone, class_exit=class_exit, method_exit=method_exit, **kws)
    if len(args) == 1: return args[0]


def checkPasswordValidity(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    import re

    # calculating the length
    length_error =  None if len(password) >= 8 else 'Length should be greater or equal to 8'

    # searching for digits
    digit_error = None if re.search(r"\d", password, flags=re.ASCII)!=None else 'Should contains at least one numeric'

    # searching for uppercase
    uppercase_error = None if re.search(r"[A-Z]", password)!=None else 'Should contains at least one Capital letter'

    # searching for lowercase
    lowercase_error = None if re.search(r"[a-z]", password)!=None else 'Should contains at least one lowercase letter'

    # searching for symbols
    symbol_error = None if re.search(r"\W", password)!=None else 'Should contains at least one special caracter'

    exclude_error = None
    try:
        sanitize_kastmenu(password, do_hide=True)
    except:
        from kwadlib.security.crypting import RE_KASTMENU
        exclude_error = 'Should not contain any of the following character: %s' % RE_KASTMENU.pattern

    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error or exclude_error)

    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
        'exclude_error': exclude_error
    }


class SimpleCrypt:
    """
    Simple Vigenere cipher.
    Thanks to: https://gist.github.com/dssstr/aedbb5e9f2185f366c6d6b50fad3e4a4
    """

    def __vigenere(
            key: str,
            text: str,
            encrypt=True
    ):
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]_`{|}~'
        result = ''

        for i in range(len(text)):
            letter_n = alphabet.index(text[i])
            key_n = alphabet.index(key[i % len(key)])

            if encrypt:
                value = (letter_n + key_n) % len(alphabet)
            else:
                value = (letter_n - key_n) % len(alphabet)

            result += alphabet[value]

        return result

    @staticmethod
    def encode(key, text):
        return SimpleCrypt.__vigenere(text=text, key=key, encrypt=True)

    @staticmethod
    def decode(key, text):
        return SimpleCrypt.__vigenere(text=text, key=key, encrypt=False)
    """
    @staticmethod
    def encode(key, string):
        import base64

        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(string[i]) + ord(key_c) % 126)
            encoded_chars.append(encoded_c)
        encoded_string = "".join(encoded_chars)
        return base64.urlsafe_b64encode(bytes(encoded_string, 'utf-8')).decode("utf-8")

    @staticmethod
    def decode(key, string):
        import base64

        string = base64.urlsafe_b64decode(string).decode("utf-8")

        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(string[i]) - ord(key_c) % 126)
            encoded_chars.append(encoded_c)
        encoded_string = "".join(encoded_chars)

        return encoded_string
    """

    @staticmethod
    def writeTempToken(name, value, dir, delay, type='second'):
        from os import path
        file = name + '_' + genUid() + '.dat'

        fd = open(path.normpath(dir + '/' + file), 'wb')
        fd.write(bytes(SimpleCrypt.flashEncode(value, delay, type=type), 'utf-8'))
        fd.close()

        return file

    @staticmethod
    def flashEncode(value, delay, type='second'):
        import base64
        """ Note: Support for LTPA like protocol:
        key negociation
        ===============
        # The key is generated minute boundary:
        from datetime import datetime
        asctime=time.time()
        asctime=int(asctime/60)
        #! t=datetime.now()
        #! asctime=str(t.year) + "%02i" % t.month + "%02i" % t.day + "%02i" % t.hour + "%02i" % t.minute
    
        # asctime is rounded by 10 to allow a ten minute resolution for this key.
        asctime=int(asctime/10)
    
        Ex:
        ---
        >>> time.time()
        1398336399.291857
        >>> int(time.time()/60)
        23305606
        >>> int(int(time.time()/60)/10)
        2330560
    
        Ex:
        Caller call with this key:ioprocess
        key: 2330560
    
        Receiver:
        Will reproduce this key: 2330560
        and 2330561 (useful when time is switching minute)
        Receiver will always try decrypte with both !!!
        """
        selfMethod = 'flashEncode'
        from hashlib import md5

        if isinstance(value, (bytes, bytearray)):value = base64.b64encode(value).decode("utf-8")
        else:value = base64.b64encode(bytes(value, 'utf-8')).decode("utf-8")

        import time, math
        # Base type inseconds:
        if type == 'second':
            base = 1
        elif type == 'minute':
            base = 60
        elif type == 'hour':
            base = 3600
        else:
            raise Exception('Class: %s, Method: %s: Unsupported Type: %s ! Supported types are: %s.' % ('SimpleCrypt', selfMethod, type, ','.join(['hour', 'minute', 'second'])))

        # Delay allowed to decrypt:
        ts = time.time()
        val = math.ceil(math.floor(ts / base) / delay)
        m = md5()
        m.update(bytes(str(val), 'utf-8'))
        secret_key = str(m.hexdigest())

        return SimpleCrypt.encode(secret_key, value)

    # adetruire.SimpleCrypt.flashEncode(value, delay, type='second')
    @staticmethod
    def flashDecode(secvalue, delay, type='second'):
        selfMethod = 'flashEncode'
        from hashlib import md5
        import time, math
        import base64
        # Base type inseconds:
        if type == 'second':
            base = 1
        elif type == 'minute':
            base = 60
        elif type == 'hour':
            base = 3600
        else:
            raise Exception('Class: %s, Method: %s: Unsupported Type: %s!  Supported types are: %s.' % ('SimpleCrypt', selfMethod, 'type', ','.join(['hour', 'minute', 'second'])))

        """
        Notice about: val = math.floor(math.floor(ts / base) / delay)
        If go with a value close to the ceiling e.g.: 0.9429414
        here: 
        secret_key: 0391b1e600338adccac5bd99f24bbcbe
        val : 341476634
        ts: 1707383174.9429414 base: 1 delay: 5
        serenity@serecat  /tmp/secret_key.back.txt 
        Received could be the upper unit (and fail):
        secret_key: 6be61a2e9bc46a96baca928bb6b03561
        val : 341476635
        ts: 1707383175.3242779 base: 1 delay: 5

        To avoid this:
        a) will take the ceil.
        b) If fail, We will check val - 1 and allow it. 
        """

        # Delay allowed to decrypt:
        ts = time.time()
        val = math.ceil(math.floor(ts / base) / delay)
        val2 = val - 1
        m = md5()
        m.update(bytes(str(val), 'utf-8'))
        secret_key = str(m.hexdigest())
        m = md5()
        m.update(bytes(str(val2), 'utf-8'))
        secret_key2 = str(m.hexdigest())

        try:
            b64 = SimpleCrypt.decode(secret_key, secvalue).strip()
            b64 = base64.b64decode(b64)
        except:
            b64 = SimpleCrypt.decode(secret_key2, secvalue).strip()
            b64 = base64.b64decode(b64)

        return  b64


class SSLCrypt:

    @staticmethod
    def loadPublicKey(pubKey):
        import rsa
        with open(pubKey) as p:
            pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(p.read().encode('utf8'))
        return pubKey

    @staticmethod
    def loadPrivateKey(privKey):
        import rsa

        with open(privKey) as p:
            privKey = rsa.PrivateKey.load_pkcs1(p.read().encode('utf8'))
        return privKey

    @staticmethod
    def decode(privKey, cvalue, doB64=False):
        import rsa
        if doB64:
            import base64
            cvalue = base64.urlsafe_b64decode(cvalue.encode("utf-8"))

        privKey = SSLCrypt.loadPrivateKey(privKey)
        return rsa.decrypt(cvalue, privKey).decode('utf-8').strip()

    @staticmethod
    def encode(pubKey, svalue, doB64=False):

        import rsa
        pubKey = SSLCrypt.loadPublicKey(pubKey)
        v = rsa.encrypt(svalue.encode('utf-8'), pubKey)

        if not doB64:return v

        import base64
        return base64.urlsafe_b64encode(v).decode("utf-8")



# See: https://stackoverflow.com/questions/27335726/how-do-i-encrypt-and-decrypt-a-string-in-python
# and: https://stackoverflow.com/questions/66097967/python-aes-256-cbc-encryption-valueerror-incorrect-aes-key-length
class AES32Crypt: # M001

    def __init__(self, salt=None, key=None, passfile=None, kfile=None):
        selfMethod='__init__'
        from os import path
        if (salt and not key) or (key and not salt): raise Exception('Parameter Error, If one of salt or key is provided both must be !')
        if (passfile and not kfile) or (kfile and not passfile): raise Exception('Parameter Error, If one of kfile or passfile is provided both must be !')
        if salt and passfile: raise Exception('Parameter Error, salt and key cannot be provided together !')
        if not salt and not passfile: raise Exception('Parameter Error, One of: salt, key or passfile, kfile must be provided !')

        if salt:
            if len(salt)!= 16:raise Exception('Incorrect Parameter salt: %s ! Length should be 16.' % str(salt))
            if len(key) != 32: raise Exception('Incorrect Parameter key: %s ! Length should be 32.' % str(key))

        elif passfile:
            if not path.isfile(passfile): raise Exception(
                'Class: %s, Method: %s: passfile: %s, should exist !' % ('Main', selfMethod, passfile))
            if not path.isfile(kfile): raise Exception(
                'Class: %s, Method: %s: kfile: %s, should exist !' % ('Main', selfMethod, kfile))

            if not passfile in P_CACHES:
                fd = open(passfile, 'rb')
                c = fd.read()
                fd.close()
                P_CACHES[passfile] = c

            password = SSLCrypt.decode(kfile, P_CACHES[passfile])
            if len(password)!=64: raise Exception('Incorrect PassPhrase should be 64 bit long !')
            salt = password[-16:]
            key = password[0:32]

        self.__salt = salt.encode('utf-8')
        self.__key = key.encode('utf-8')
        self.enc_dec_method = 'utf-8'

    def encryptFile(self, file):
        """
        This will encrypt a text or binary file
        """
        from os import path
        if not path.isfile(file): raise Exception('File: %s should Exist !' % file)
        outfile = path.splitext(file)[0] + '.enc'

        with open(file, "rb") as f:
            crypted = self.encrypt(f.read())

            fd = open(outfile, 'w')
            fd.write(crypted)
            fd.close()

        return outfile

    def decryptFile(self, file):
        """
        This will decrypt a text file
        """
        from os import path
        if not path.isfile(file): raise Exception('File: %s should Exist !' % file)
        outfile = path.splitext(file)[0] + '.dec'

        with open(file, "r") as f:
            message = f.read()
            clear = self.decrypt(message)

            fd = open(outfile, 'wb')
            # fd.write(b64decode(clear))
            fd.write(clear)
            fd.close()

        return outfile

    def encrypt(self, toenc):
        """
        This will encrypt a text or binary
        """
        from Crypto.Cipher import AES
        try:
            toenc = base64.b64encode(toenc).decode('utf8')
            aes_obj = AES.new(self.__key, AES.MODE_CFB, self.__salt)
            hx_enc = aes_obj.encrypt(toenc.encode('utf8'))
            mret = base64.b64encode(hx_enc).decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Encryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Encryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)

    def decrypt(self, todec):
        """
        This will decrypt a text string
        """
        from Crypto.Cipher import AES

        try:
            aes_obj = AES.new(self.__key, AES.MODE_CFB, self.__salt)
            str_tmp = base64.b64decode(todec.encode(self.enc_dec_method))
            str_dec = aes_obj.decrypt(str_tmp)
            mret = str_dec.decode(self.enc_dec_method)
            mret = base64.b64decode(mret)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Decryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Decryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)



def padTo16(value):
    l = len(value)
    mod, left = divmod(l, 16)
    if left == 0:return value

    more = (mod + 1) * 16 - l
    return value + more * '0'

class AES256Crypt:
    """
    This will Symetrically encrypt/decrypt.
    value must be a multiple of 16 length block.
    value must be ascii.
    key and iv (are also needed for decrypting) must be provided if not they will be generated
    and they should be retreived for use for decryption.
    """

    @staticmethod
    def encrypt(value, key=None, iv=None):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from os import urandom
        import base64
        doReturnKey = doReturnIv = False, False
        if key==None:key = urandom(32)
        if iv==None:iv = urandom(16)

        # Check Value:
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            raise Exception('value must be ascii !')

        if len(value)/16 != int(len(value)/16):
            raise Exception('value length must be a multiple of 16 !')

        # Check keys:
        if len(key)!=32:raise Exception('key length must be: 32 !')
        if len(iv)!=16:raise Exception('iv length must be: 16 !')

        if key == None:
            doReturnKey = True
            key = urandom(32)

        if iv == None:
            doReturnIv = True
            iv = urandom(16)

        cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        ct = encryptor.update(value.encode('utf8')) + encryptor.finalize()

        return base64.b64encode(ct).decode('utf8'), key if doReturnKey else None, iv if doReturnIv else None,

    @staticmethod
    def decrypt(cvalue, key, iv):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        if len(key)!=32:raise Exception('key length must be: 32 !')
        if len(iv)!=16:raise Exception('iv length must be: 16 !')

        try:
            cvalue = base64.b64decode(cvalue)
        except:
            raise Exception('cvalue must be base64 encoded !')

        cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))

        decryptor = cipher.decryptor()
        value = decryptor.update(cvalue) + decryptor.finalize()

        return value.decode('utf8')



def setSecidToFile(secid_md5, secid, port, temp_dir=None):
    """
    Write Kdealer secid and port from Stdin.
    The expected Syntax is: kealer:<secid>,<port>
    """
    from os import path, remove
    from kwadlib.tools import getTempDir
    if temp_dir==None:temp_dir = getTempDir()

    file = path.normpath(temp_dir + '/' + secid_md5 + '.dat')
    secval = SimpleCrypt.flashEncode('kdealer:' + secid + ',' + str(port), 5, type='second')

    """ todo: remove:
    fd = open('/tmp/setSecidToFile.txt', 'w')
    fd.write(file)
    fd.close()
    """

    fd = open(file, 'w')
    fd.write(secval)
    fd.close()



def getOptSecidFromFile(name, temp_dir=None):
    selfMethod='getOptSecidFromFile'
    if name == None: return None, None
    """
    Reads Kdealer secid and port from Stdin.
    The expected Syntax is: kealer:<secid>,<port>
    """
    from os import path, remove
    secid = None
    port = None

    from kwadlib.tools import getTempDir
    if temp_dir==None:temp_dir = getTempDir()

    file = path.normpath(temp_dir + '/' + name + '.dat')
    if not path.isfile(file):
        return None, None

    fd = open(file)
    secval = fd.read()
    fd.close()
    remove(file)

    # <=> secval = input()

    secval = secval.strip()

    if not (secval == None or secval == ''):
        val = SimpleCrypt.flashDecode(secval, 5, type='second').decode('utf-8')
        if val.startswith('kdealer:'):
            # Syntax: kdealer:<secid>,<port>
            secid, port = val[8:].split(',')
            port = int(port)
            if secid == None or secid == '':
                raise Exception('Class: %s, Method: %s: Unconsitent secid and port value !' % ('Main', selfMethod))
            elif port == None or port == '':
                raise Exception('Class: %s, Method: %s: Unconsitent secid and port value !' % ('Main', selfMethod))

    return secid, port


def ldap_slappasswd(password):
    """
    LDAP SHA1 Password:
    """
    selfMethod = 'ldap_slappasswd'
    import pexpect

    try:
        cmd = '/usr/sbin/slappasswd'
        child = pexpect.spawn(cmd)
        # New password:
        child.expect("assword:", timeout=3)
        child.sendline(password)
        # Re-enter new password:
        child.expect("assword:", timeout=3)
        child.sendline(password)

        data = child.read().decode("utf-8")
        child.close()
    except:
        raise

    data = data.strip()

    return data

def expectSSlKey(cmd, passfile, keyfile, message="assword:", twice=False, verbose=0):
    """
    Beware spaces into cmd line argument must be replace by %20 !!
    """
    selfMethod = 'expectSSlKey'
    import pexpect, warnings
    from os import path
    if not path.isfile(passfile):raise Exception('Class: %s, Method: %s: passfile: %s, should exist !' % ('Main', selfMethod, passfile))
    if not path.isfile(keyfile):raise Exception('Class: %s, Method: %s: keyfile: %s, should exist !' % ('Main', selfMethod, keyfile))
    if message == None: message = "assword:"
    if verbose >= 10:
        print ('->Class: Main, Method: %s Trying to run command: %s' % (selfMethod, cmd))

    if not passfile in P_CACHES:
        import subprocess
        fd = open(passfile, 'rb')
        c = fd.read()
        fd.close()
        P_CACHES[passfile] = c

    xpassword = SSLCrypt.decode(keyfile, P_CACHES[passfile])

    data=None
    child=None
    try:
        child = pexpect.spawn(cmd)
        # New password:
        # - insttead of child.expect(message, timeout=3) use the following line to avoid: pexecpt.EOF exception. See: https://9to5answer.com/pexpect-eof-end-of-file-eof-exception-style-platform
        child.expect([pexpect.TIMEOUT, message, pexpect.EOF], timeout=1)
        child.sendline(xpassword)
        # Re-enter new password:
        if twice:
            child.expect([pexpect.TIMEOUT, message, pexpect.EOF], timeout=1)
            child.sendline(xpassword)

        data = child.read().decode("utf-8")

        if data.find(xpassword) >=0:data = None # Dont show password
        rc = child.exitstatus
        child.close()
        child.terminate()

        # See: https://pexpect.readthedocs.io/en/stable/api/pexpect.html
        rc = child.exitstatus
        signal = child.signalstatus
        if rc != 0 or signal != None:
            if rc != 0:
                if verbose>=10:
                    # ++
                    before = child.before
                    if before!=None:
                        before = child.before.decode("utf-8").replace(xpassword, '').strip() # remove password from before
                        if data == None:data=''
                        if before!=None:data+=before
                    warnings.warn('Class: Main, Method: %s Error running command: %s\nWith data:\n%s' % (selfMethod, cmd, data))
                raise NoneZeroRCException(rc, 'Main', selfMethod, data=data)
            if signal != None:
                raise EndedBySignal(signal, 'Main', selfMethod)

    except pexpect.exceptions.TIMEOUT:
        if data == None and child!=None:data = child.before.decode("utf-8").replace(xpassword, '').strip() # remove password from before
        if verbose>=10:
            warnings.warn('Class: Main, Method: %s TimeOut reached running command: %s' % (selfMethod, cmd))
        raise TimeOutException('Main', selfMethod, data=data)
    except:
        raise

    if data!=None:data = data.strip()

    if verbose >= 10:
        print ('<-Class: Main, Method: %s Sucess running command: %s.' % (selfMethod, cmd))
    return data

def expect(cmd, value, message="assword:", twice=False, verbose=0):
    """
    Beware spaces into cmd line argument must be replace by %20 !!
    """
    selfMethod = 'expect'
    if cmd == None:raise Exception('Parameter cmd cannot be None !')
    if value == None:raise Exception('Parameter value cannot be None !')

    import pexpect, warnings
    if verbose >= 10:
        print ('Class: Main, Method: %s Trying to run command: %s' % (selfMethod, cmd))

    if message == None: message = "assword:"

    data=None
    child=None
    try:
        child = pexpect.spawn(cmd)
        # New password:
        # - insttead of child.expect(message, timeout=3) use the following line to avoid: pexecpt.EOF exception. See: https://9to5answer.com/pexpect-eof-end-of-file-eof-exception-style-platform
        child.expect([pexpect.TIMEOUT, message, pexpect.EOF], timeout=1)
        child.sendline(value)

        # Re-enter new password:
        if twice:
            # Rem: supports a parameter: async_:
            # child.expect([pexpect.TIMEOUT, message, pexpect.EOF], timeout=1)
            child.sendline(value)

        data = child.read().decode("utf-8")

        if data.find(value) >=0:data = None # Dont show password

        rc = child.exitstatus
        child.close()
        child.terminate()

        # See: https://pexpect.readthedocs.io/en/stable/api/pexpect.html
        rc = child.exitstatus
        signal = child.signalstatus
        if rc != 0 or signal != None:
            if rc != 0:
                if verbose>=10:
                    # ++
                    before = child.before
                    if before!=None:
                        before = child.before.decode("utf-8").replace(value, '').strip() # remove password from before
                        if data == None:data=''
                        if before!=None:data+=before
                    warnings.warn('Class: Main, Method: %s Error running command: %s\nWith data:\n%s' % (selfMethod, cmd, data))
                raise NoneZeroRCException(rc, 'Main', selfMethod, data=data)
            if signal != None:
                raise EndedBySignal(signal, 'Main', selfMethod)

    except pexpect.exceptions.TIMEOUT:
        if data == None and child != None: data = child.before.decode("utf-8").replace(value, '').strip() # remove password from before
        if verbose>=10:
            warnings.warn('Class: Main, Method: %s TimeOut reached running command: %s' % (selfMethod, cmd))
        raise TimeOutException('Main', selfMethod, data=data)
    except:
        raise

    if data!=None:data = data.strip()

    if verbose >= 10:
        print ('<-Class: Main, Method: %s Sucess running command: %s.' % (selfMethod, cmd))
    return data



class TimeOutException(Exception):
    def __init__(self, fromClass, fromMethod, data=None):
            more=''
            if data!=None:more=' ' + data
            self.__value = 'FromClass: %s, FromMethod: %s: The Command failed with TimeOut reached !%s' % (fromClass, fromMethod, more)

    def __str__(self):
        return self.__value
class NoneZeroRCException(Exception):
    def __init__(self, rc, fromClass, fromMethod, data=None):
            # Dont show the rc because of the pexpect (message) this is not the command return code but something else > 0.
            self.__value = 'FromClass: %s, FromMethod: %s: The Command failed with a NonZerror Return Code !' % (fromClass, fromMethod)
            if data!=None:self.data = data
            else:self.data = None

    def __str__(self):
        return self.__value
class EndedBySignal(Exception):
    def __init__(self, signal, fromClass, fromMethod):
            self.__value = 'FromClass: %s, FromMethod: %s: The Command was ended by signal: %s !' % (fromClass, fromMethod, signal)

    def __str__(self):
        return self.__value


def checkPort(host, port):
    self_funct = 'checkPort'

    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
    except:
        raise Exception(self_funct + ': This Host: %s Port: %s is not open !' % (str(host), str(port)))


def sshNoPassword(host, user, password, type='rsa', ssh_port=22, verbose=0):
    self_funct='Main/sshNoPassword'
    from kwadlib import default
    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
    from kwadlib.tools import check_output
    from subprocess import TimeoutExpired
    from os import path
    sanitize(class_exit='Main', method_exit='sshNoPassword', **{'user': user})
    sanitize_kastmenu(do_hide=True, class_exit='Main', method_exit='sshNoPassword', **{'password': password})
    sanitize_hostorip(class_exit='Main', method_exit='sshNoPassword', **{'host': host})
    KEY_TYPES = ('rsa', 'dsa', 'ecdsa', 'ed25519')
    if ssh_port == 22:SSH_PORT = ''
    else:SSH_PORT = ' -p %s' % str(ssh_port)
    if type not in KEY_TYPES:
        raise Exception(self_funct + ': Unsupported type: %s ! Allowed types are: %s.' % (type, ', '.join(KEY_TYPES)))

    checkPort(host, ssh_port)

    # Check current User is kastmenu:
    # -----------------------------
    cuser = getUser()
    if cuser != default.KAST_USER:
        raise Exception(self_funct + ': is allowed only to user: kastmenu. Not for user: %s !' % cuser)

    # Check is keys are already generated ?
    # -------------------------------------
    """
    serenity@serenity:~$ ls  ~/.ssh/
        known_hosts
        id_rsa.pub
        id_rsa
    """
    if verbose>=10:print (self_funct + ': Check is keys are already generated ?')
    hdir = getUserHomeDir()
    if not (path.isfile(hdir + '/.ssh/' + 'id_' + type) and
        path.isfile(hdir + '/.ssh/' + 'id_' + type + '.pub')):

        # Otherwise Gen:
        # --------------
        cmd = "ssh-keygen -q -t %s -N '' <<< $'\ny' >/dev/null 2>&1" % type
        #1:
        p = Popen(cmd, shell=True, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_PIPE, executable='/bin/bash')
        err, out = p.communicate()
        ret = p.wait()

        if p.returncode!=0:
            output = out.decode('utf-8').rstrip()
            err = err.decode('utf-8').rstrip()
            if err: output+= '\n' + err
            raise Exception('Unable to run command: %s ! Returned code is: %s, SubException is: %s' % (cmd, p.returncode, output))

    # Accept Remote Fingerprint knownhost:
    # ------------------------------------
    if verbose>=10:print(self_funct + ': Accept Remote Fingerprint knownhost:')
    import pexpect, time
    cmd = 'ssh %s %s@%s ls' % (SSH_PORT, user, host)
    try:
        #1!
        child = pexpect.spawn(cmd, encoding='utf-8', timeout=1)
        bytes = child.expect('[[fingerprint]]')
        bytes = child.sendline('yes')
        data = child.read()
        child.close()
        rc = child.exitstatus

        if rc not in (0, None): raise Exception('Error: %s Running pexpect command ! Returned code is: %s.%s' % (cmd, str(rc), data if data else ''))
    except pexpect.exceptions.TIMEOUT:
        pass
        # raise Exception('Timeout reached !')
    except Exception as e:
        pass
        # raise Exception('Error pexpect command ! SubException is %s' % str(e))


    # Remove current key from Remote authorized_keys:
    # -----------------------------------------------
    if verbose>=10:print(self_funct + ': Remove current key from Remote Authorized_keys (if Exists):')
    # 1:
    ## prev_key = check_output(['sudo', '-u', default.KAST_USER, 'cat', '/home/%s/.ssh/id_%s.pub' % (default.KAST_USER, type)]).decode('utf-8').strip()
    prev_key = check_output(['cat', '/home/%s/.ssh/id_%s.pub' % (default.KAST_USER, type)]).decode('utf-8').strip()
    if user == 'root':home='/root'
    else:home = '/home/%s' % user
    cmd = """ssh {ssh_port} {user}@{host}  "grep -v - <<EOF  {home}/.ssh/authorized_keys  > {home}/.ssh/authorized_keys
{prev_key}
EOF"
    """.format(
        ssh_port=SSH_PORT, user=user, host=host, home=home, prev_key=prev_key)
    #1:
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    try:
        stdout, stderr = p.communicate(timeout=1.1)
        ret = p.wait(timeout=1.1)
        stdout_stderr = stdout
    except:
        pass

    # Copy to RemoteHost:
    # -------------------
    # sudo -u kastmenu cat /home/kastmenu/.ssh/id_rsa.pub
    if verbose>=10:print(self_funct + ": Copy %s ssh id to Remote Host's Authorized_keys:" % default.KAST_USER)
    import pexpect
    send_pass = password + '\n'
    # 1:
    cmd = 'ssh-copy-id %s -f %s@%s' % (SSH_PORT, user, host)

    # Eof see: https://stackoverflow.com/questions/39557925/pexpect-eof-end-of-file-eof-exception-style-platform
    try:
        # 1:
        child = pexpect.spawn(cmd, encoding='utf-8', timeout=3, logfile=None)
        # bytes = child.expect([pexpect.TIMEOUT, 'password:'])
        bytes = child.expect([pexpect.TIMEOUT, 'password:', pexpect.EOF])
        bytes = child.sendline(send_pass)
        # time.sleep(1)
        data = child.read()
        child.close()
        rc = child.exitstatus

        if rc not in (0, None):
            raise Exception('Error: %s Running pexpect command !%s' % (str(rc), data if data else ''))
    except pexpect.exceptions.TIMEOUT:
        raise Exception('Unable to run pexpect: command: %s ! SubException is Timeout reached ! User/Password may not be correct.' % cmd)
    except Exception as e:
        raise Exception('Unable to run pexpect: command: %s ! SubException is %s' % (cmd, str(e)))
    except:
        raise
    finally:
        child.close()
        # Switch Terminal back to stty echo:
        check_output(('stty', 'echo'))

    # Test:
    # -----
    if verbose>=10:print(self_funct + ': Testing no password Access:')
    cmd = "ssh  %s  %s@%s hostname -I" % (SSH_PORT, user, host)
    #1:
    p = Popen(cmd, shell=True, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_PIPE, executable='/bin/bash')
    try:
        out, err = p.communicate(timeout=2)  # will raise error and kill any process that runs longer than 2 seconds
        ret = p.wait()
    except TimeoutExpired as e:
        p.kill()
        out, err = p.communicate()
    finally:
        if p.returncode!=0:
            output = ''
            try:
                output = out.decode('utf-8').rstrip()
                err = err.decode('utf-8').rstrip()
                if err: output += '\n' + err
            except:
                pass
            raise Exception('Unable to run command: %s ! Returned code is: %s, SubException is: %s' % (cmd, p.returncode, output))

def rmSshNoPassword(host, user, type='rsa', ssh_port=22, verbose=0):
    self_funct='Main/sshNoPassword'
    from kwadlib import default
    from kwadlib.tools import Popen, SUBPROCESS_STDOUT, SUBPROCESS_PIPE
    from kwadlib.tools import check_output
    from subprocess import TimeoutExpired
    sanitize_hostorip(host)
    KEY_TYPES = ('rsa', 'dsa', 'ecdsa', 'ed25519')
    if ssh_port == 22:SSH_PORT = ''
    else:SSH_PORT = ' -p %s' % str(ssh_port)
    if type not in KEY_TYPES:
        raise Exception(self_funct + ': Unsupported type: %s ! Allowed types are: %s.' % (type, ', '.join(KEY_TYPES)))

    checkPort(host, ssh_port)

    # Check current User is kastmenu:
    # -----------------------------
    cuser = getUser()
    if cuser != default.KAST_USER:
        raise Exception(self_funct + ': is allowed only to user: kastmenu. Not for user: %s !' % cuser)

    # Remove current key from Remote authorized_keys:
    # -----------------------------------------------
    if verbose>=10:print(self_funct + ': Remove current key from Remote Authorized_keys (if Exists):')
    # 1:
    ## prev_key = check_output(['sudo', '-u', default.KAST_USER, 'cat', '/home/%s/.ssh/id_%s.pub' % (default.KAST_USER, type)]).decode('utf-8').strip()
    prev_key = check_output(['cat', '/home/%s/.ssh/id_%s.pub' % (default.KAST_USER, type)]).decode('utf-8').strip()
    if user == 'root':home='/root'
    else:home = '/home/%s' % user
    cmd = """ssh {ssh_port} {user}@{host}  "grep -v - <<EOF  {home}/.ssh/authorized_keys  > {home}/.ssh/authorized_keys
{prev_key}
EOF"
    """.format(
        ssh_port=SSH_PORT, user=user, host=host, home=home, prev_key=prev_key)

    #1:
    p = Popen(cmd, stdout=SUBPROCESS_PIPE, stderr=SUBPROCESS_STDOUT, universal_newlines=True, shell=True)
    try:
        stdout, stderr = p.communicate(timeout=1.1)
        ret = p.wait(timeout=1.1)
        stdout_stderr = stdout
    except:
        ret = 1

    return ret, stdout_stderr

def sha256(value):
    """ In bash:
    serenity@serenity:~$ echo $s | sha256sum
    2c04f611eb2b14dbe8485f1032de08cb69a97e8c11ca410b77ec309f0106a858  -
    serenity@serenity:~$ echo $s | openssl dgst -sha256
    (stdin)= 2c04f611eb2b14dbe8485f1032de08cb69a97e8c11ca410b77ec309f0106a858
    """
    from hashlib import sha256
    if isinstance(value, bytes):return sha256(value).digest().hex()
    return sha256(value.encode('utf-8')).digest().hex()
