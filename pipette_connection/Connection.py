from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks


class Connection(ApplicationSession):
    camera = None
    subscription = None
    arduino_uri = u'com.pipette.arduino'
    ui_uri = u'com.pipette.ui'

    @inlineCallbacks
    def onJoin(self, details):
        self.camera = self.config.extra["com_object"]
        self.subscription = yield self.subscribe(self.incoming_from_arduino, self.arduino_uri)
        print("Subscribed to {} with {}".format(self.arduino_uri, self.subscription.id))

    def onLeave(self, details):
        print("LEAVING")
        print(details)

    def onDisconnect(self):
        print("DISCONNECTED")

    def incoming_from_arduino(self, payload):
        coords = self.camera.get_current_coords()
        if coords is not None:
            print(coords['x'], coords['y'], payload)
            self.publish(self.ui_uri, {'x':coords['x'], 'y':coords['y'], 'color': payload})