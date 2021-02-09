import sys, os, re, json, random, time, threading, hashlib

class HTTPAuthHead():
    """Attaches HTTP Authentication Header to the given Request object."""

    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        #self.nonce = nonce
        # Keep state in per-thread local storage
        self._thread_local = threading.local()
        #print(username, password)
        #required nonce and uri values are generated by making get request with need_auth=1 to the url
        #self.res = sess.get("http://192.168.0.1/devinfo?need_auth=1").headers
        ###print(self.res)
        self._thread_local.init = True
        self._thread_local.last_nonce = ''  #Updated at Last
        self._thread_local.nonce_count = 0
        self._thread_local.chal = {}    #Values to be supplied
        self._thread_local.pos = None
        self._thread_local.num_401_calls = None

    def build_basic_header(self):
    	fin = base64.b64encode(('%s:%s' % (self.username, self.password)).encode('ascii'))
    	print("Basic %s" % fin.decode())

    def build_digest_header(self):

        method = "POST"
        uri = ""		# end-point
        realm = "domain"
        nonce =  		# Updated in the auth request 
        qop = "auth"
        algorithm = 'MD5'
        '''opaque = self._thread_local.chal.get('opaque')'''
        auth_url = links['auth']
        hash_utf8 = None

        #print(realm, nonce, qop)

        if algorithm is None:
            _algorithm = 'MD5'
        else:
            _algorithm = algorithm.upper()
        # lambdas assume digest modules are imported at the top level
        if _algorithm == 'MD5' or _algorithm == 'MD5-SESS':
            def md5_utf8(x):
                #Check if the X type is String
                if isinstance(x, str):
                    x = x.encode('utf-8')
                return hashlib.md5(x).hexdigest()
            hash_utf8 = md5_utf8	#Giving the final Func to trigger 

        #To Maintain HAsh Format For the Digest    
        KD = lambda s, d: hash_utf8("%s:%s" % (s, d))

        if hash_utf8 is None:
            return None

        #Logic Starts
        A1 = '%s:%s:%s' % (self.username, realm, self.password)
        A2 = '%s:%s' % (method, uri)

        HA1 = hash_utf8(A1)
        HA2 = hash_utf8(A2)

        if nonce == self._thread_local.last_nonce:
            self._thread_local.nonce_count += 1
        else:
            self._thread_local.nonce_count = 1

        #NC Value
        ncvalue = '%08x' % self._thread_local.nonce_count
        #print(ncvalue)

        s = str(self._thread_local.nonce_count).encode('utf-8')
        s += nonce.encode('utf-8')
        s += time.ctime().encode('utf-8')
        s += os.urandom(8)

        #Cnounce Value
        cnonce = (hashlib.sha1(s).hexdigest()[:16])
        #print(cnonce)
        if _algorithm == 'MD5-SESS':
            HA1 = hash_utf8('%s:%s:%s' % (HA1, nonce, cnonce))

        if not qop:
            respdig = KD(HA1, "%s:%s" % (nonce, HA2))
        elif qop == 'auth' or 'auth' in qop.split(','):
            noncebit = "%s:%s:%s:%s:%s" % (
                nonce, ncvalue, cnonce, 'auth', HA2
            )
            respdig = KD(HA1, noncebit)
        else:
            # XXX handle auth-int.
            return None

        self._thread_local.last_nonce = nonce

        # XXX should the partial digests be encoded too?
        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s", qop="auth", nc=%s, cnonce="%s"' % (self.username, realm, nonce, uri, respdig, ncvalue, cnonce)
           # base += ', qop="auth", nc=%s, cnonce="%s"' % (ncvalue, cnonce)
        print('Digest %s' % (base))