"""
K6GTE, CW interface abstraction
Email: michael.bridak@gmail.com
GPL V3
"""

from xmlrpc.client import ServerProxy, Error
import socket
import logging

if __name__ == "__main__":
    print("I'm not the program you are looking for.")

logger = logging.getLogger("cwinterface")


class CW:
    """

    An interface to cwdaemon and PyWinkeyerSerial

    servertype: int 1=cwdaemon, 2=pywinkeyer, 3=rigctld

    """

    def __init__(self, servertype: int, host: str, port: int) -> None:
        self.servertype = servertype
        self.cat = None
        self.host = host
        self.port = port
        self.speed = 20
        self.winkeyer_functions = []
        if self.servertype == 2:
            with ServerProxy(f"http://{self.host}:{self.port}") as proxy:
                try:
                    self.winkeyer_functions = proxy.system.listMethods()
                    logger.debug("%s", f"{self.winkeyer_functions}")
                except Error as exception:
                    logger.info(
                        "http://%s:%s, xmlrpc error: %s",
                        self.host,
                        self.port,
                        exception,
                    )
                except ConnectionRefusedError:
                    logger.info(
                        "http://%s:%s, xmlrpc Connection Refused", self.host, self.port
                    )

    def sendcw(self, texttosend):
        """sends cw to k1el"""
        logger.debug(f"{texttosend=} {self.servertype=}")
        if texttosend:
            if self.servertype == 2:
                self._sendcw_xmlrpc(texttosend)
            if self.servertype == 1:
                self._sendcw_udp(texttosend)
            if self.servertype == 3 and self.cw is not None:
                self._sendcwcat(texttosend)

    def _sendcw_xmlrpc(self, texttosend):
        """sends cw to xmlrpc"""
        logger.debug("xmlrpc: %s", texttosend)
        if texttosend:
            with ServerProxy(f"http://{self.host}:{self.port}") as proxy:
                try:
                    proxy.k1elsendstring(texttosend)
                except Error as exception:
                    logger.debug(
                        "http://%s:%s, xmlrpc error: %s",
                        self.host,
                        self.port,
                        exception,
                    )
                except ConnectionRefusedError:
                    logger.debug(
                        "http://%s:%s, xmlrpc Connection Refused", self.host, self.port
                    )

    def _sendcw_udp(self, texttosend):
        """send cw to udp port"""
        logger.debug("UDP: %s", texttosend)
        if texttosend:
            server_address_port = (self.host, self.port)
            # bufferSize          = 1024
            udp_client_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM
            )
            udp_client_socket.sendto(bytes(texttosend, "utf-8"), server_address_port)

    def _sendcwcat(self, texttosend):
        """..."""

    def set_winkeyer_speed(self, speed):
        """doc"""
        with ServerProxy(f"http://{self.host}:{self.port}") as proxy:
            try:
                if "setspeed" in self.winkeyer_functions:
                    proxy.setspeed(speed)
            except Error as exception:
                logger.info(
                    "http://%s:%s, xmlrpc error: %s", self.host, self.port, exception
                )
            except ConnectionRefusedError:
                logger.info(
                    "http://%s:%s, xmlrpc Connection Refused", self.host, self.port
                )
