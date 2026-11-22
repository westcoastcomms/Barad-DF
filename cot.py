# Barad-DF CoT output: builds Cursor-on-Target XML for ATAK and sends it by UDP
import math
import socket
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape, quoteattr

EARTH_RADIUS_M = 6371008.8


def destination_point(lat_deg, lon_deg, bearing_deg, distance_m):
    """Point reached by travelling distance_m from (lat, lon) along a true bearing (great circle)."""
    lat1, lon1, brg = (math.radians(v)
                       for v in (lat_deg, lon_deg, bearing_deg))
    d = distance_m / EARTH_RADIUS_M
    lat2 = math.asin(math.sin(lat1) * math.cos(d) +
                     math.cos(lat1) * math.sin(d) * math.cos(brg))
    lon2 = lon1 + math.atan2(math.sin(brg) * math.sin(d) * math.cos(lat1),
                             math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return math.degrees(lat2), (math.degrees(lon2) + 540) % 360 - 180


def cot_time(dt):
    """CoT timestamps are UTC, ISO 8601, with milliseconds and a trailing Z."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def build_sensor_event(uid, lat, lon, hae, callsign, stale_s=30, now=None):
    """Position marker for the receiver itself (friendly ground sensor)."""
    now = now or datetime.now(timezone.utc)
    t, stale = cot_time(now), cot_time(now + timedelta(seconds=stale_s))
    return (f'<event version="2.0" uid={quoteattr(uid)} type="a-f-G-E-S" time="{t}" start="{t}" stale="{stale}" how="m-g">'
            f'<point lat="{lat:.7f}" lon="{lon:.7f}" hae="{hae:.1f}" ce="9999999.0" le="9999999.0"/>'
            f'<detail><contact callsign={quoteattr(callsign)}/></detail></event>')


def build_lob_event(uid, lat, lon, hae, true_bearing_deg, length_m, callsign, remarks, stale_s=10, now=None):
    """A freeform line (u-d-f) from the receiver along a true bearing. Reusing the uid updates the line in place."""
    now = now or datetime.now(timezone.utc)
    t, stale = cot_time(now), cot_time(now + timedelta(seconds=stale_s))
    end_lat, end_lon = destination_point(lat, lon, true_bearing_deg, length_m)
    return (f'<event version="2.0" uid={quoteattr(uid)} type="u-d-f" time="{t}" start="{t}" stale="{stale}" how="m-g">'
            f'<point lat="{lat:.7f}" lon="{lon:.7f}" hae="{hae:.1f}" ce="9999999.0" le="9999999.0"/>'
            f'<detail>'
            f'<link point="{lat:.7f},{lon:.7f},{hae:.1f}"/>'
            f'<link point="{end_lat:.7f},{end_lon:.7f},{hae:.1f}"/>'
            f'<strokeColor value="-65536"/><strokeWeight value="3.0"/>'
            f'<contact callsign={quoteattr(callsign)}/><remarks>{escape(remarks)}</remarks>'
            f'<archive/><labels_on value="true"/>'
            f'</detail></event>')


class CotSender:
    """Sends CoT XML as UDP datagrams, to ATAK's multicast group or to any address."""

    def __init__(self, address, port, interface_ip=None, ttl=1):
        self.destination = (address, port)
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        if interface_ip:
            self.sock.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))

    def send(self, xml):
        self.sock.sendto(xml.encode("utf-8"), self.destination)

    def close(self):
        self.sock.close()
