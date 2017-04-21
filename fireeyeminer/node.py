import logging
import json

import requests

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)

class urllistMiner(BasePollerFT):
    def configure(self):
        super(urllistMiner, self).configure()

        self.polling_timeout = self.config.get('polling_timeout', 20)
        self.verify_cert = self.config.get('verify_cert', True)

        self.fireeye_nx = self.config.get('fireeye_nx', None)
        if self.fireeye_nx is None:
            raise ValueError('%s - Fireeye NX/CMS URL is required' % self.name)

        self.url = 'http://%s/URLlist.txt' & (self.fireeye_nx)
        self.url = 'http://www.edfauler.com/urllist.txt'

    def _build_iterator(self, item):
        callbacks = []
        malicious = []
        malicious_sw = 0
        callbacks_sw = 0
        # builds the request and retrieves the page
        rkwargs = dict(
            stream=False,
            verify=self.verify_cert,
            timeout=self.polling_timeout
        )

        r = requests.get(
            self.url,
            **rkwargs
        )

        try:
            r.raise_for_status()
        except:
            LOG.debug('%s - exception in request: %s %s',
                      self.name, r.status_code, r.content)
            raise

        # parse the page
        r = r.text.split('\n')
        
        for line in r:
            line = line.rstrip('\r\n')
            if "End" in line:
                malicious_sw = 0
                callbacks_sw = 0
            if malicious_sw == 1:
                value = line.split("=")
                if value[0].strip() == "url":
                    malicious.append(value[1])
            if callbacks_sw == 1:
                value = line.split("=")
                if value[0].strip() == "url":
                    callbacks.append(value[1])
            if "define condition FireEye_Callbacks" in line:
                callbacks_sw = 1
            if "define condition FireEye_MaliciousURL" in line:
                malicious_sw = 1
        return callbacks
    
    def _process_item(self, item):
        mycallback = item
        if mycallback is None:
            LOG.error('%s - no data-context-item-id attribute', self.name)
            return []

        indicator = '{}'.format(mycallback)
        value = {
            'type': 'URL',
            'confidence': 100
        }

        return [[indicator, value]]