from multiprocessing.managers import BaseManager
from multiprocessing import Process
from pipette_connection.Connection import Connection
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from camera_tracker import CameraTracker
import cv2

######################################################
################### GENERAL VARS #####################

URL = u'ws://127.0.0.1:8080/ws'
REALM = u'realm1'

class ComObject:
    cx = None
    cy = None

    def get_current_coords(self):
        if self.cx is None or self.cy is None:
            return None

        return {'x':self.cx, 'y':self.cy}

    def set_current_coords(self, cx, cy):
        self.cx = cx
        self.cy = cy

class MyManager(BaseManager): pass
MyManager.register('comObject', ComObject)

def get_manager():
    m = MyManager()
    m.start()
    return m

######################################################


def web_thread(com_object):
    runner = ApplicationRunner(
        url=URL,
        realm=REALM,
        extra={"com_object": com_object}
    )
    runner.run(Connection)


def main():
    threading_manager = get_manager()
    com_object = threading_manager.comObject()

    # starting threads
    try:
        web_p = Process(target=web_thread,args=(com_object,))
        web_p.start()

        camera = CameraTracker(com_object)
        m = camera.calibrate()
        camera.ir_loop(m)

        print("Camera terminated, killing everything")
        web_p.terminate()
        cv2.destroyAllWindows()
        exit(1)

    except KeyboardInterrupt:
        print("keyboard int. shutting down.")


if __name__ == "__main__":
    main()