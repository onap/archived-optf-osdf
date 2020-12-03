from consul.base import Timeout
from consul.tornado import Consul
import json
from osdf.logging.osdf_logging import debug_log
from tornado.gen import coroutine
from tornado.ioloop import IOLoop


class Config(object):
    def __init__(self, loop, osdf_final_config):
        self.config = osdf_final_config
        osdf_config = self.config['osdf_config']
        self.consul = Consul(host=osdf_config['consulHost'], port=osdf_config['consulPort'],
                             scheme=osdf_config['consulScheme'], verify=osdf_config['consulVerify'],
                             cert=osdf_config['consulCert'])
        result = json.dumps(self.config)
        self.consul.kv.put("osdfconfiguration", result)
        loop.add_callback(self.watch)

    @coroutine
    def watch(self):
        index = None
        while True:
            try:
                index, data = yield self.consul.kv.get('osdfconfiguration', index=index)
                if data is not None:
                    self.update_config(data)
            except Timeout:
                pass
            except Exception as e:
                debug_log.debug('Exception Encountered {}'.format(e))

    def update_config(self, data):
        new_config = json.loads(data['Value'].decode('utf-8'))
        osdf_deployment = new_config['osdf_config']
        osdf_core = new_config['common_config']
        self.config['osdf_config'].update(osdf_deployment)
        self.config['common_config'].update(osdf_core)
        debug_log.debug("updated config {}".format(new_config))
        debug_log.debug("value changed")


def call_consul_kv(osdf_config):
    osdf_final_config = {
        'osdf_config': osdf_config.deployment,
        'common_config': osdf_config.core
    }
    io_loop = IOLoop()
    io_loop.make_current()
    IOLoop.current(instance=False)
    _ = Config(io_loop, osdf_final_config)
    io_loop.start()
