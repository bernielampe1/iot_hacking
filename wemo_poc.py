#!/usr/bin/python

import re, urllib2

class wemo:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def status(self):
        return self._send('Get', 'BinaryState', 'basicevent')

    def name(self):
        return self._send('Get', 'FriendlyName', 'basicevent')

    def signal(self):
        return self._send('Get', 'SignalStrength', 'basicevent')

    def iconurl(self):
        return self._send('Get', 'IconURL', 'basicevent')

    def loglevel(self, level):
        return self._send('Set', 'LogLevelOption', 'basicevent', {'Level':level})

    def firmwareversion(self):
        return self._send('Get', 'FirmwareVersion', 'firmwareupdate')

    def firmwareupdate(self, URL):
        return self._send('Update', 'Firmware', 'firmwareupdate',
                          {'URL':URL,
                           'NewFirmwareVersion':'WeMo_WW_2.00.10077.PVT-OWRT-Jarden',
                           'ReleaseDate':'1-May-2016',
                           'Signature':0,
                           'DownloadStartTime':0,
                           'WithUnsignedImage':1 })

    def _get_header_xml(self, method, obj, service):
        method = method + obj
        return '"urn:Belkin:service:%s:1#%s"' % (service, method)

    def _get_body_xml(self, method, obj, service, values={}):
        method = method + obj
        body = '<u:%s xmlns:u="urn:Belkin:service:%s:1">' % (method, service)
        for k in values.keys():
            body += '<%s>%s</%s>' % (k, values[k], k)
        body += '</u:%s>' % method
        return body

    def _send(self, method, obj, service, values={}):
        body_xml = self._get_body_xml(method, obj, service, values)
        header_xml = self._get_header_xml(method, obj, service)
        result = self._try_send(self.ip, self.port, body_xml, header_xml, obj, service)
        return result

    def _try_send(self, ip, port, body, header, obj, service):
        try:
            request = urllib2.Request('http://%s:%s/upnp/control/%s1' % (ip, port, service))
            request.add_header('Content-type', 'text/xml; charset="utf-8"')
            request.add_header('SOAPACTION', header)
            request_body = '<?xml version="1.0" encoding="utf-8"?>'
            request_body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            request_body += '<s:Body>%s</s:Body></s:Envelope>' % body
            request.add_data(request_body)
            result = urllib2.urlopen(request, timeout=3)
            return self._extract(result.read(), obj)
        except Exception as e:
            print str(e)
            return None

    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
        return response

target = wemo('10.22.22.1', 49152)
print "status = %s" % target.status()
print "signal = %s" % target.signal()
print "name = %s" % target.name()
print "iconurl = %s" % target.iconurl()
print "firmware version = %s" % target.firmwareversion()
#print "firmware update= %s" % target.firmwareupdate("http://10.22.22.197/firmware.bin.gpg")

