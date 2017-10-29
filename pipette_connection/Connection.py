from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks


class Connection(ApplicationSession):
    camera = None
    subscription = None
    arduino_uri = u'com.p.a'
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

    def clamp(self, x):
        return max(0, min(x, 255))

    def incoming_from_arduino(self, r, g, b):
        coords = self.camera.get_current_coords()
        color = "#{0:02x}{1:02x}{2:02x}".format(self.clamp(r), self.clamp(g), self.clamp(b))
        if coords is not None:
            print(coords['x'], coords['y'], r, g, b)
            self.publish(self.ui_uri, {'x':coords['x'], 'y':coords['y'], 'color': color})