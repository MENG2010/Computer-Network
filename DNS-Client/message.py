"""
Message object encodes and decodes message.

@author: YMENG
"""
import random
import struct


class Message(object):
    def encode(self, domain, IPv6):
        """Encode the message."""
        self.header = Header()
        self.question = Question()
        self.question.construct_question(domain, IPv6)
        
        msg = b''
        msg += self.header.encode()
        msg += self.question.encode()
        
        return msg
    

    def decode(self, msg):
        """Decode the message."""
        self.header = Header()
        offset = self.header.decode(msg)
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additionals = []
        
        for _ in range(self.header.qdcount):
            self.questions.append(Question())
            offset = self.questions[-1].decode(msg, offset)
        
        for _ in range(self.header.ancount):
            self.answers.append(ResourceRecord())
            offset = self.answers[-1].decode(msg, offset)
            
        for _ in range(self.header.nscount):
            self.authorities.append(ResourceRecord())
            offset = self.authorities[-1].decode(msg, offset)
            
        for _ in range(self.header.arcount):
            self.additionals.append(ResourceRecord())
            offset = self.additionals[-1].decode(msg, offset)


    def has_answer(self):
        """Whether receiving answers from server."""
        return len(self.answers) > 0
    
    
    def display(self):
        """Display the message."""
        print('+-----------------------------------------------+')
        print('|                    HEADER                     |')
        print('+-----------------------------------------------+')
        self.header.display()

        print('+-----------------------------------------------+')
        print('|                   QUESTION                    |')
        print('+-----------------------------------------------+')
        for i in range(self.header.qdcount):
            print(f'| QUESTION[{i}]:')
            self.questions[i].display()

        print('+-----------------------------------------------+')
        print('|                  ANSWER                       |')
        print('+-----------------------------------------------+')
        for i in range(self.header.ancount):
            print(f'| ANSWER[{i}]:')
            self.answers[i].display()

        print('+-----------------------------------------------+')
        print('|                  AUTHORITY                    |')
        print('+-----------------------------------------------+')
        for i in range(self.header.nscount):
            print(f'| AUTHORITY_RR[{i}]:')
            self.authorities[i].display()

        print('+-----------------------------------------------+')
        print('|                 ADDITIONAL                    |')
        print('+-----------------------------------------------+')
        for i in range(self.header.arcount):
            print(f'| ADDITIONAL_RR[{i}]:')
            self.additionals[i].display()
        
    
    def get_ips(self):
        """Display the desired answer: IP."""
        ips = ''
        for ans in self.answers:
            # IPv4 or IPv6
            if ans.rtype == 1 or ans.rtype == 28:
                ips += ans.rdata.ip + '\n'
        
        return ips
        

class Header(object):
    def __init__(self):
        # 16-bit identifier, initialized as a random number.
        self.id = random.randint(0, 65535)
        # 1-bit indicator for query or response. 0 for query, 1 for response
        self.qr = 0
        # 4-bit indicator for the kind of query in this message.
        # Check the opcode_name function for details.
        self.opcode = 0
        # 1-bit indicator for authoritative answer.
        # 0 for not authoritative, 1 for authoritative
        self.aa = 0
        # 1-bit indicator for whether the message is truncated due to the capacity limit.
        self.tc = 0 
        # 1-bit indicator for whether to query recursively.
        # Note: I make the client query from server recursively 
        #       in order to improve the success rate of querying.
        #       Otherwise, the success rate of non-recursive query is very low (< 30%).
        self.rd = 1
        # 1-bit indicator for whether recursion is available.
        self.ra = 0
        # 3-bit indicator for reserved fields.
        self.z = 0
        # 4-bit response code. Check the response_code function for details.
        self.rcode = 0
        # 16-bit integer specifying the number of entries in the question section.
        self.qdcount = 1
        # 16-bit integer specifying the number of resource records in the answer section.
        self.ancount = 0
        # 16-bit integer specifying the number of name server resource records in the authority records section.
        self.nscount = 0
        # 16-bit integer specifying the number of resource records in the additional records section.
        self.arcount = 0


    def encode(self):
        """Encode the header."""
        encoded = struct.pack('>H', self.id)
        fields = self.qr << 15 | self.opcode << 11 | self.aa << 10 | self.tc << 9 | self.rd << 8 | self.ra << 7 | self.rcode
        encoded += struct.pack('>H', fields)
        encoded += struct.pack('>H', self.qdcount)
        encoded += struct.pack('>H', self.ancount)
        encoded += struct.pack('>H', self.nscount)
        encoded += struct.pack('>H', self.arcount)
        
        return encoded


    def decode(self, response):
        """Decode the header."""
        self.id = struct.unpack('>H', response[0:2])[0]
        fields = struct.unpack('>H', response[2:4])[0]
        self.rcode = (fields & 15)
        fields >>= 7
        self.ra = (fields & 1)
        fields >>= 1
        self.rd = (fields & 1)
        fields >>= 1
        self.tc = (fields & 1)
        fields >>= 1
        self.aa = (fields & 1)
        fields >>= 1
        self.opcode = (fields & 15)
        fields >>= 4
        self.qr = fields
        self.qdcount = struct.unpack('>H', response[4:6])[0]
        self.ancount = struct.unpack('>H', response[6:8])[0]
        self.nscount = struct.unpack('>H', response[8:10])[0]
        self.arcount = struct.unpack('>H', response[10:12])[0]
        
        return 12  # return the offset of the next section


    def display(self):
        """Print the message header."""
        print(f'| Message ID:\t\t{self.id}')
        print(f'| Query/Response:\t{msg_type(self.qr)}')
        print(f'| Opcode:\t\t{opcode_name(self.opcode)}')
        print(f'| Authoritative:\t{bool(self.aa)}')
        print(f'| Is TranCation:\t{bool(self.tc)}')
        print(f'| Recursive Mode:\t{bool(self.rd)}')
        print(f'| Recursion Available:\t{bool(self.ra)}')
        print(f'| Response Code:\t({self.rcode}, {response_code(self.rcode)})')
        print(f'| Question Count:\t{self.qdcount}')
        print(f'| Answer Count:\t\t{self.ancount}')
        print(f'| Authority Count:\t{self.nscount}')
        print(f'| Additional Count:\t{self.arcount}')
    

class Question(object):
    
    def construct_question(self, name, IPv6):
        # field containing a domain name that is the query name.
        # dynamic length, ends with `\0x00`.
        self.name = name
        # 2-bit integer indicates as RR.
        self.rtype = 28 if IPv6 else 1
        # 2-bit integer indicates as RR.
        self.rclass = 1
        
    
    def encode(self):
        """Encode the question."""
        name = self.name
        if name.endswith('.'):
            name = name[:-1]
        
        encoded = b''
        for domain in name.split('.'):
            encoded += struct.pack('B', len(domain))
            encoded += bytes(domain, 'utf-8')
        # question name ends with a null byte
        encoded += b'\x00'
        
        encoded += struct.pack('>H', self.rtype)
        encoded += struct.pack('>H', self.rclass)
        
        return encoded
    
    
    def decode(self, msg, offset):
        """Decode the question."""
        offset, self.name = _decode_data(msg, offset)
        self.rtype = struct.unpack('>H', msg[offset:offset+2])[0]
        offset += 2
        self.rclass = struct.unpack('>H', msg[offset:offset+2])[0]
        offset += 2
        
        return offset
    
    
    def display(self):
        """Display the content of the question."""
        print(f'|\tName:\t\t{self.name}')
        print(f'|\tType:\t\t{query_type(self.rtype)}')
        print(f'|\tClass:\t\t{self.rclass}')
    

class ResourceRecord(object):
    def _create_rdata(self, msg, offset):
        """Create the resource data."""
        rdata = msg[offset:offset+self.rdlength]
        
        if self.rtype == 1:  # IPv4
            self.rdata = AResourceData(rdata)
        elif self.rtype == 28:  # IPv6
            self.rdata = AAAAResourceData(rdata)
        else: 
            # we only want IP addresses, 
            # therefore, we do not need to distinguish other types of records.
            self.rdata = DummyResourceData(rdata)
        
    
    def decode(self, msg, offset):
        """Decode the resource record."""
        offset, self.name = _decode_data(msg, offset)
        self.rtype = struct.unpack('>H', msg[offset:offset+2])[0]
        offset += 2
        self.rclass = struct.unpack('>H', msg[offset:offset+2])[0]
        offset += 2
        self.ttl = struct.unpack('>I', msg[offset:offset+4])[0]
        offset += 4
        self.rdlength = struct.unpack('>H', msg[offset:offset+2])[0]
        offset += 2
        
        self._create_rdata(msg, offset)
        return offset + self.rdlength
    

    def display(self):
        """Display the Resource Record."""
        print(f'|\tName:\t\t{self.name}')
        print(f'|\tType:\t\t{query_type(self.rtype)}')
        print(f'|\tClass:\t\t{self.rclass}')
        print(f'|\tTTL:\t\t{self.ttl}')
        print(f'|\tRDLength:\t{self.rdlength}')
        self.rdata.display()


class AResourceData(object):
    """Resource data for `A` record."""
    def __init__(self, data):
        ip = struct.unpack('BBBB', data)
        self.ip = '.'.join([str(x) for x in ip])
        
    def display(self):
        """Display the resource data."""
        print(f'|\t`A`:\t\t{self.ip}')
    

class AAAAResourceData(object):
    """Resource data for `AAAA` record."""
    def __init__(self, data):
        self.data = data
        processed = ''
        for byte in data:
            processed += str(hex(256 + byte))[3:]
        
        self.ip = ''
        for i in range(0, 8, 4):
            value = processed[i*4:i*4+4]
            for j in range(4):
                if value[j] != '0':
                    value = value[j:]
                    break
                if j == 3:
                    value = ''
            self.ip += value + ':'
        self.ip = self.ip[:-1]

        
    def display(self):
        """Display the resource data."""
        print(f'| `AAAA`:\t\t{self.ip}')
        

class DummyResourceData(object):
    """Resource data."""
    def __init__(self, data):
        # Ignore other types of records and
        # leave the data not decoded.
        # I call it dummy resource data.
        self.data = data
        
    def display(self):
        """Display the resource data."""
        print(f'| `Dummy (undecoded raw)`:\t\t{self.data}')
        

def query_type(type_id):
    """Return type name given a type id.
    Reference:
    https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml
    """
    type_id = int(type_id)
    try:
        qtype = {
            1: 'A', 2: 'NS', 3: 'MD', 4: 'MF', 5: 'CNAME', 
            6: 'SOA', 7: 'MB', 8: 'MG', 9: 'MR', 10: 'NULL',
            11: 'WKS', 12: 'PTR', 13: 'HINFO', 14: 'MINFO', 15: 'MX',
            16: 'TXT', 17: 'RP', 18: 'AFSDB', 19: 'X25', 20: 'ISDN',
            21: 'RT', 22: 'NSAP', 23: 'NSAP-PTR', 24: 'SIG', 25: 'KEY',
            26: 'PX', 27: 'GPOS', 28: 'AAAA', 29: 'LOC', 30: 'NXT',
            31: 'EID', 32: 'NIMLOC', 33: 'SRV', 34: 'ATMA', 35: 'NAPTR',
            36: 'KX', 37: 'CERT', 38: 'A6', 39: 'DNAME', 40: 'SINK',
            41: 'OPT', 42: 'APL', 43: 'DS', 44: 'SSHFP', 45: 'IPSECKEY',
            46: 'RRISG', 47: 'NSEC', 48: 'DNSKEY', 49: 'DHCID', 50: 'NSEC3',
            51: 'NSEC3PARAM', 52: 'TLSA', 53: 'SMIMEA', 55: 'HIP', 
            56: 'NINFO', 57: 'RKEY', 58: 'TALINK', 59: 'CDS', 60: 'CDNSKEY', 
            61: 'OPENPGPKEY', 62: 'CSYNC', 63: 'ZONEMD', 64: 'SVCB', 65: 'HTTPS',
            99: 'SPF', 100: 'UINFO', 
            101: 'UID', 102: 'GID', 103: 'UNSPEC', 104: 'NID', 105: 'L32',
            106: 'L64', 107: 'LP', 108: 'EUI48', 109: 'EUI64', 249: 'TKEY', 250: 'TSIG',
            251: 'IXFR', 252: 'AXFR', 253: 'MAILB', 254: 'MAILA', 255: '*',
            256: 'URI', 257: 'CAA', 258: 'AVC', 259: 'DOA', 260: 'AMTRELAY',
            32769: 'DLV', 65535: 'RESERVED'
        }[type_id]
    except:
        if 66 <= type_id <= 98 or \
            110 <= type_id <= 248 or \
            261 <= type_id <= 32767 or \
            32770 <= type_id <= 65279:
            qtype = 'UNASSIGNED'
        elif 65280 <= type_id <= 65534:
            qtype = 'PRIVATE USE'
        else:
            qtype = 'UNKNOWN'
        
    return qtype


def opcode_name(opcode):
    """Return the opcode name given an opcode."""
    try:
        opname = {
            0: 'QUERY',
            1: 'IQUERY',
            2: 'STATUS',
        }[int(opcode)]
    except:
        opname = 'UNKNOWN'
    
    return opname


def msg_type(qr):
    """Return message type given a qr."""
    try:
        mtype = {
            0: 'QUERY',
            1: 'RESPONSE',
        }[int(qr)]
    except:
        mtype = 'INVALID'
        
    return mtype


def response_code(rcode):
    """Return response code given a rcode.
    Reference: https://help.dnsfilter.com/hc/en-us/articles/4408415850003-DNS-Return-Codes
    """
    try:
        desc = {
            0: 'NO ERROR',
            1: 'FORMAT ERROR',
            2: 'SERVER FAILURE',
            3: 'NAME ERROR',
            4: 'NOT IMPLEMENTED',
            5: 'REFUSED',
            6: 'YXDOMAIN',
            7: 'XRRSET',
            8: 'NOTAUTH',
            9: 'NOTZONE',
        }[int(rcode)]
    except:
        desc = 'UNKNOWN'
    
    return desc


def _decode_data(data, offset):
    """Decodes data."""
    index = offset
    decoded = ''
    offset = 0

    while data[index] != 0:
        value = data[index]
        if (value >> 6) == 3:
            next_value = struct.unpack('>H', data[index:index+2])[0]

            if offset == 0:
                offset = index + 2
            index = next_value ^ (3 << 14)
        else:
            decoded += data[index+1:index+value+1].decode('utf-8') + '.'
            index += value + 1

    if offset == 0:
        offset = index + 1
    return (offset, decoded[:-1])
