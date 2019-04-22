from lxml.etree import fromstring, tostring
import datetime as dt
import listen
import sys

voe_preliminary = """<?xml version="1.0" ?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
 version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS181101ab-1-Preliminary">
    <Who>
        <Date>2018-11-01T22:34:49</Date>
        <Author>
            <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
        </Author>
    </Who>
    <What>
        <Param name="internal" dataType="int" value="0">
            <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
        </Param>
        <Param name="Packet_Type" dataType="int" value="150">
            <Description>The Notice Type number is assigned/used within GCN, eg type=150 is an LVC_PRELIMINARY notice</Description>
        </Param>
        <Param name="Pkt_Ser_Num" dataType="string" value="1"/>
        <Param name="GraceID" dataType="string" value="MS181101ab" ucd="meta.id">
            <Description>Identifier in GraceDB</Description>
        </Param>
        <Param name="AlertType" dataType="string" value="Preliminary" ucd="meta.version">
            <Description>VOEvent alert type</Description>
        </Param>
        <Param name="HardwareInj" dataType="int" value="0" ucd="meta.number">
            <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
        </Param>
        <Param name="OpenAlert" dataType="int" value="1" ucd="meta.number">
            <Description>Indicates that this event is an open alert if 1, no if 0</Description>
        </Param>
        <Param name="EventPage" dataType="string" value="https://example.org/superevents/MS181101ab/view/" ucd="meta.ref.url">
            <Description>Web page for evolving status of this GW candidate</Description>
        </Param>
        <Param name="Instruments" dataType="string" value="H1,L1" ucd="meta.code">
            <Description>List of instruments used in analysis to identify this event</Description>
        </Param>
        <Param name="FAR" dataType="float" value="9.11069936486e-14" ucd="arith.rate;stat.falsealarm" unit="Hz">
            <Description>False alarm rate for GW candidates with this strength or greater</Description>
        </Param>
        <Param name="Group" dataType="string" value="CBC" ucd="meta.code">
            <Description>Data analysis working group</Description>
        </Param>
        <Param name="Pipeline" dataType="string" value="gstlal" ucd="meta.code">
            <Description>Low-latency data analysis pipeline</Description>
        </Param>
        <Param name="Search" dataType="string" value="MDC" ucd="meta.code">
            <Description>Specific low-latency search</Description>
        </Param>
        <Group type="GW_SKYMAP" name="bayestar">
            <Param name="skymap_fits" dataType="string" value="https://emfollow.docs.ligo.org/userguide/_static/bayestar.fits.gz" ucd="meta.ref.url">
                <Description>Sky Map FITS</Description>
            </Param>
        </Group>
        <Group type="Classification">
            <Description>
                Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), or terrestrial (noise)
            </Description>
            <Param name="BNS" dataType="float" value="0.95" ucd="stat.probability">
                <Description>Probability that the source is a binary neutron star merger</Description>
            </Param>
            <Param name="NSBH" dataType="float" value="0.01" ucd="stat.probability">
                <Description>Probability that the source is a neutron star - black hole merger</Description>
            </Param>
            <Param name="BBH" dataType="float" value="0.03" ucd="stat.probability">
                <Description>Probability that the source is a binary black hole merger</Description>
            </Param>
            <Param name="Terrestrial" dataType="float" value="0.01" ucd="stat.probability">
                <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
            </Param>
        </Group>
        <Group type="Properties">
            <Description>
                Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger
            </Description>
            <Param name="HasNS" dataType="float" value="0.95" ucd="stat.probability">
                <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
            </Param>
            <Param name="HasRemnant" dataType="float" value="0.91" ucd="stat.probability">
                <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
            </Param>
        </Group>
    </What>
    <WhereWhen>
        <ObsDataLocation>
            <ObservatoryLocation id="LIGO Virgo"/>
            <ObservationLocation>
                <AstroCoordSystem id="UTC-FK5-GEO"/>
                <AstroCoords coord_system_id="UTC-FK5-GEO">
                    <Time>
                        <TimeInstant>
                            <ISOTime>2018-11-01T22:22:46.654437</ISOTime>
                        </TimeInstant>
                    </Time>
                </AstroCoords>
            </ObservationLocation>
        </ObsDataLocation>
    </WhereWhen>
    <How>
        <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
        <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
        <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
    </How>
    <Description>Report of a candidate gravitational wave event</Description>
</voe:VOEvent>
"""

voe_initial = """<?xml version="1.0" ?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
 version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS181101ab-2-Initial">
    <Who>
        <Date>2018-11-01T22:36:25</Date>
        <Author>
            <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
        </Author>
    </Who>
    <What>
        <Param name="internal" dataType="int" value="0">
            <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
        </Param>
        <Param name="Packet_Type" dataType="int" value="151">
            <Description>The Notice Type number is assigned/used within GCN, eg type=151 is an LVC_INITIAL notice</Description>
        </Param>
        <Param name="Pkt_Ser_Num" dataType="string" value="2"/>
        <Param name="GraceID" dataType="string" value="MS181101ab" ucd="meta.id">
            <Description>Identifier in GraceDB</Description>
        </Param>
        <Param name="AlertType" dataType="string" value="Initial" ucd="meta.version">
            <Description>VOEvent alert type</Description>
        </Param>
        <Param name="HardwareInj" dataType="int" value="0" ucd="meta.number">
            <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
        </Param>
        <Param name="OpenAlert" dataType="int" value="1" ucd="meta.number">
            <Description>Indicates that this event is an open alert if 1, no if 0</Description>
        </Param>
        <Param name="EventPage" dataType="string" value="https://example.org/superevents/MS181101ab/view/" ucd="meta.ref.url">
            <Description>Web page for evolving status of this GW candidate</Description>
        </Param>
        <Param name="Instruments" dataType="string" value="H1,L1" ucd="meta.code">
            <Description>List of instruments used in analysis to identify this event</Description>
        </Param>
        <Param name="FAR" dataType="float" value="9.11069936486e-14" ucd="arith.rate;stat.falsealarm" unit="Hz">
            <Description>False alarm rate for GW candidates with this strength or greater</Description>
        </Param>
        <Param name="Group" dataType="string" value="CBC" ucd="meta.code">
            <Description>Data analysis working group</Description>
        </Param>
        <Param name="Pipeline" dataType="string" value="gstlal" ucd="meta.code">
            <Description>Low-latency data analysis pipeline</Description>
        </Param>
        <Param name="Search" dataType="string" value="MDC" ucd="meta.code">
            <Description>Specific low-latency search</Description>
        </Param>
        <Group type="GW_SKYMAP" name="bayestar">
            <Param name="skymap_fits" dataType="string" value="https://emfollow.docs.ligo.org/userguide/_static/bayestar.fits.gz" ucd="meta.ref.url">
                <Description>Sky Map FITS</Description>
            </Param>
        </Group>
        <Group type="Classification">
            <Description>
                Source classification: binary neutron star (BNS), neutron star-black hole (NSBH), binary black hole (BBH), or terrestrial (noise)
            </Description>
            <Param name="BNS" dataType="float" value="0.95" ucd="stat.probability">
                <Description>Probability that the source is a binary neutron star merger</Description>
            </Param>
            <Param name="NSBH" dataType="float" value="0.01" ucd="stat.probability">
                <Description>Probability that the source is a neutron star - black hole merger</Description>
            </Param>
            <Param name="BBH" dataType="float" value="0.03" ucd="stat.probability">
                <Description>Probability that the source is a binary black hole merger</Description>
            </Param>
            <Param name="Terrestrial" dataType="float" value="0.01" ucd="stat.probability">
                <Description>Probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)</Description>
            </Param>
        </Group>
        <Group type="Properties">
            <Description>
                Qualitative properties of the source, conditioned on the assumption that the signal is an astrophysical compact binary merger
            </Description>
            <Param name="HasNS" dataType="float" value="0.95" ucd="stat.probability">
                <Description>Probability that at least one object in the binary has a mass that is less than 3 solar masses</Description>
            </Param>
            <Param name="HasRemnant" dataType="float" value="0.91" ucd="stat.probability">
                <Description>Probability that a nonzero mass was ejected outside the central remnant object</Description>
            </Param>
        </Group>
    </What>
    <WhereWhen>
        <ObsDataLocation>
            <ObservatoryLocation id="LIGO Virgo"/>
            <ObservationLocation>
                <AstroCoordSystem id="UTC-FK5-GEO"/>
                <AstroCoords coord_system_id="UTC-FK5-GEO">
                    <Time>
                        <TimeInstant>
                            <ISOTime>2018-11-01T22:22:46.654437</ISOTime>
                        </TimeInstant>
                    </Time>
                </AstroCoords>
            </ObservationLocation>
        </ObsDataLocation>
    </WhereWhen>
    <How>
        <Description>Candidate gravitational wave event identified by low-latency analysis</Description>
        <Description>H1: LIGO Hanford 4 km gravitational wave detector</Description>
        <Description>L1: LIGO Livingston 4 km gravitational wave detector</Description>
    </How>
    <Description>Report of a candidate gravitational wave event</Description>
</voe:VOEvent>
"""

voe_retraction = """<?xml version="1.0" ?>
<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0"
xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd"
 version="2.0" role="test" ivorn="ivo://gwnet/LVC#MS181101ab-4-Retraction">
    <Who>
        <Date>2018-11-01T23:36:23</Date>
        <Author>
            <contactName>LIGO Scientific Collaboration and Virgo Collaboration</contactName>
        </Author>
    </Who>
    <What>
        <Param name="internal" dataType="int" value="0">
            <Description>Indicates whether this event should be distributed to LSC/Virgo members only</Description>
        </Param>
        <Param name="Packet_Type" dataType="int" value="164">
            <Description>The Notice Type number is assigned/used within GCN, eg type=164 is an LVC_RETRACTION notice</Description>
        </Param>
        <Param name="Pkt_Ser_Num" dataType="string" value="4"/>
        <Param name="GraceID" dataType="string" value="MS181101ab" ucd="meta.id">
            <Description>Identifier in GraceDB</Description>
        </Param>
        <Param name="AlertType" dataType="string" value="Preliminary" ucd="meta.version">
            <Description>VOEvent alert type</Description>
        </Param>
        <Param name="HardwareInj" dataType="int" value="0" ucd="meta.number">
            <Description>Indicates that this event is a hardware injection if 1, no if 0</Description>
        </Param>
        <Param name="OpenAlert" dataType="int" value="1" ucd="meta.number">
            <Description>Indicates that this event is an open alert if 1, no if 0</Description>
        </Param>
        <Param name="EventPage" dataType="string" value="https://example.org/superevents/MS181101ab/view/" ucd="meta.ref.url">
            <Description>Web page for evolving status of this GW candidate</Description>
        </Param>
    </What>
    <WhereWhen>
        <ObsDataLocation>
            <ObservatoryLocation id="LIGO Virgo"/>
            <ObservationLocation>
                <AstroCoordSystem id="UTC-FK5-GEO"/>
                <AstroCoords coord_system_id="UTC-FK5-GEO">
                    <Time>
                        <TimeInstant>
                            <ISOTime>2018-11-01T22:22:46.654437</ISOTime>
                        </TimeInstant>
                    </Time>
                </AstroCoords>
            </ObservationLocation>
        </ObsDataLocation>
    </WhereWhen>
    <Citations>
        <EventIVORN cite="retraction">ivo://gwnet/LVC#MS181101ab-1-Preliminary</EventIVORN>
        <EventIVORN cite="retraction">ivo://gwnet/LVC#MS181101ab-2-Initial</EventIVORN>
        <EventIVORN cite="retraction">ivo://gwnet/LVC#MS181101ab-3-Update</EventIVORN>
        <Description>Determined to not be a viable GW event candidate</Description>
    </Citations>
</voe:VOEvent>
"""

root = fromstring(voe_preliminary)
root.attrib['role'] = 'drill'

now = dt.datetime.now()
# Set the event time to be ~10 min before now
event_time = now - dt.timedelta(minutes=11)
root.find("./WhereWhen//ISOTime").text = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

# Set grace id according to today's date and D for drill.
alphabet = 'abcdefghijklmnopqrstuvwxyz'
ab = "".join([alphabet[event_time.hour],
         alphabet[event_time.minute % len(alphabet)]])
grace_id = 'DS' + event_time.strftime("%y%m%d") + ab
root.find("./What//Param[@name='GraceID']").attrib['value'] = grace_id

file_lines = []
found_first = False
with open("drill_info.txt", "r") as f:
    for aline in f.readlines():
        if aline[0] == "#" or aline[0] == "\n":
            file_lines.append(aline)
            continue
        if not found_first:
            retracted, event_page, skymapfits_url, \
                bnsprob, nsbhprob, bbhprob, nsprob, remprob = aline.split()
            file_lines.append("# " + aline)
            found_first = True
            continue
        file_lines.append(aline)

with open("drill_info.txt", "w") as f:
    for aline in file_lines:
        f.write(aline)

if not found_first:
    sys.exit(1)

# Set data from what's in the drill file
will_be_retracted = (retracted[0] == 'Y')
root.find("./What//Param[@name='EventPage']").attrib['value'] = event_page
root.find("./What//Param[@name='skymap_fits']").attrib['value'] = skymapfits_url
root.find("./What//Param[@name='BNS']").attrib['value'] = bnsprob
root.find("./What//Param[@name='NSBH']").attrib['value'] = nsbhprob
root.find("./What//Param[@name='BBH']").attrib['value'] = bbhprob
root.find("./What//Param[@name='HasNS']").attrib['value'] = nsprob
root.find("./What//Param[@name='HasRemnant']").attrib['value'] = remprob

# Set GCN time to now
root.find("./Who//Date").text = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

payload = tostring(root)

listen.init_logger()
listen.process_gcn(payload, root)

# Wait 2 min, send Initial or Retraction or Update
import time
time.sleep(120)

# ---- Send second GCN ----
root = None
if will_be_retracted:
    root = fromstring(voe_retraction)
else:
    root = fromstring(voe_initial)
root.attrib['role'] = 'drill'

# Set the event time
root.find("./WhereWhen//ISOTime").text = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
# Set grace id
root.find("./What//Param[@name='GraceID']").attrib['value'] = grace_id
root.find("./What//Param[@name='EventPage']").attrib['value'] = event_page

if not will_be_retracted:
    # Set data from what's in the drill file
    root.find("./What//Param[@name='skymap_fits']").attrib['value'] = skymapfits_url
    root.find("./What//Param[@name='BNS']").attrib['value'] = bnsprob
    root.find("./What//Param[@name='NSBH']").attrib['value'] = nsbhprob
    root.find("./What//Param[@name='BBH']").attrib['value'] = bbhprob
    root.find("./What//Param[@name='HasNS']").attrib['value'] = nsprob
    root.find("./What//Param[@name='HasRemnant']").attrib['value'] = remprob

# Set GCN time to now
root.find("./Who//Date").text = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

payload = tostring(root)

listen.process_gcn(payload, root)
