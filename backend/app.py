import datetime
import json
import re
import traceback
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app) # Enable CORS for all routes (important for your Vue app)

#Starting Logging

def nowUTC():
    """returns current UTC time as timezone aware datetime"""
    return datetime.datetime.now(datetime.UTC)

def nowLocal():
    """returns current local time as timezone aware datetime"""
    return datetime.datetime.now().astimezone()

scriptstart = nowUTC()
LOG_LOCATION = '_logs/'
log_file = LOG_LOCATION + scriptstart.strftime('%Y-%m-%d %H-%M-%S') + '.log'

print(nowLocal(), "Script Start")

def alivetime():
    """returns how long the script has been running"""
    delta = nowUTC() - scriptstart
    days = delta.days
    hours = int(delta.seconds / 3600)
    minutes = int(delta.seconds / 60) - (hours * 60)
    seconds = delta.seconds - (hours * 3600) - (minutes * 60)
    days = str(days)
    hours = "0" + str(hours)
    minutes = "0" + str(minutes)
    seconds = "0" + str(seconds)
    out = days+":"+hours[-2:]+":"+minutes[-2:]+":"+seconds[-2:]
    return "Uptime: "+out

def check_time_format(time_string):
    """Checks if a string matches the "HH:MM" format.

    Args:
      time_string: The string to check.

    Returns:
      True if the string matches the format, False otherwise.
    """
    pattern = r"^\d{2}:\d{2}$"
    return bool(re.match(pattern, time_string))



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

bus_station_stops = ['1090BSTN01',
                    '1090BSTN02',
                    '1090BSTN03',
                    '1090BSTN04',
                    '1090BSTN05',
                    '1090BSTN06',
                    '1090BSTN07',
                    '1090BSTN08',
                    '1090BSTN09',
                    '1090BSTN10',
                    '1090BSTN11',
                    '1090BSTN12',
                    '1090BSTN13',
                    '1090BSTN14',
                    '1090BSTN15',
                    '1090BSTN16',
                    '1090BSTN17',
                    '1090BSTN18',
                    '1090BSTN19',
                    '1090BSTN20',
                    '1090BSTN21',
                    '1090BSTN22',
                    '1090BSTN23',
                    '1090BSTN24',
                    '1090BSTN25',
                    '109000022166',
                    '109000009330',
                    '109000022155',
                    '109000022165']

bus_station_request =   {
    '109GDDCCBS01':{
        'type':'station'
    },
    '109000022150':{},
    '109000022155':{
        'filter': {
            'type':'is_not',
            'key':'destination_stop/atco_code',
            'value':bus_station_stops
        }
    }
}

normal_stops = {
    '109000009334':{},
    '1090DDVS1302':{},
    '1090DDVS1224':{},
    '109000022164':{},
    '109000022165':{},
    '109000022171':{
        'filter':{
            'type':'is_not',
            'key':'destination_stop/atco_code',
            'value':bus_station_stops
        }
    }
}

def get_departures(stops_request = None):
    """gets bus departures from specified stops"""

    # --- Sets default stops for function if none are specified ---
    if stops_request is None:
        stops_request = normal_stops

    stops_request_data = {}

    # --- Opens and store _data/stops.json ---
    #     This contains previously fetched metadata about the stops
    try:
        with open('_data/stops.json', encoding="utf-8") as f:
            stops_data = json.loads(f.read())
        print(nowLocal(), "Successfully loaded _data/stops.json")
        print(nowLocal(), json.dumps(stops_data, indent=4, default=str))
    except (json.JSONDecodeError, FileNotFoundError):
        stops_data = {}


    # --- Opens and store _data/trips.json ---
    #     This contains previously fetched metadata about the individual journeys
    try:
        with open('_data/trips.json', encoding="utf-8") as f:
            trips_data = json.loads(f.read())
        print(nowLocal(), "Successfully loaded _data/trips.json")
    except (json.JSONDecodeError, FileNotFoundError):
        trips_data = {}

    for stop,extras in stops_request.items():
        stops_request_data[stop] = {}
        if extras.get('type') == 'station':    # if the stop is actually a station
            print("getting departures from "+'https://bustimes.org/stations/'+str(stop)+'/')
            stops_request_data[stop]['html'] = requests.get('https://bustimes.org/stations/'+str(stop)+'/', headers=headers, timeout=10).text

        else:
            if stops_data.get(stop) == None or stops_data.get(stop).get('long_name') == None:
                print("getting metadata from "+'https://bustimes.org/api/stops/'+str(stop)+'/?format=json')     # Gets stop metadata if it doesn't already exist
                stops_request_data[stop] = json.loads(requests.get('https://bustimes.org/api/stops/'+str(stop)+'/?format=json', headers=headers, timeout=10).text)
            else:
                stops_request_data[stop] = stops_data[stop]
            print("getting departures from "+'https://bustimes.org/stops/'+str(stop)+'/')                         # Gets departure page
            stops_request_data[stop]['html'] = requests.get('https://bustimes.org/stops/'+str(stop)+'/', headers=headers, timeout=10).text

        stops_request_data[stop]['extras'] = extras

        stops_data[stop] = stops_request_data[stop]

    departures_full_data = []
    departures_summary = []


    for stop,info in stops_request_data.items():
        soup = BeautifulSoup(info['html'], 'html.parser')
        print('parcing departures for',stop,info.get('long_name') or '(Stop Name Not Found)')
        try:
            for i in soup.findAll(id='departures'):
                for j in i.findAll('table'):
                    for l in j.findAll('tr'):
                        if l == j.findAll('tr')[0]:
                            table_headers = []
                            for m in l.findAll('th'):
                                table_headers.append(m.text.strip())
                            #print(table_headers)
                            continue
                        try:
                            departure = {}
                            departure['display'] = {}
                            departure['service'] = {}
                            departure['stop'] = {'icon': None,
                                                    'indicator': None,
                                                    'bay': None}
                            departure['stop'].update(info)

                            departure['page_service'] = {
                                    'slug' : l.findAll('td')[0].a['href'].replace('/services/',''),
                                    'line_name' : l.findAll('td')[0].a.text
                                }
                            departure['page_destination'] = l.findAll('td')[1].text.strip()
                            departure['page_scheduled'] = l.findAll('td')[2].text.strip()

                            departure['page_trip_id'] = l.findAll('td')[2].a['href'].replace('/trips/','')

                            try:
                                departure['trip'] =  trips_data[departure['page_trip_id']]
                            except KeyError:
                                print("getting trip data from "+'https://bustimes.org/api/trips/'+departure['page_trip_id']+'/?format=json')
                                trips_data[departure['page_trip_id']] = json.loads(requests.get('https://bustimes.org/api/trips/'+departure['page_trip_id']+'/?format=json', headers=headers, timeout=10).text)
                                departure['trip'] = trips_data[departure['page_trip_id']]

                            destination_id = str(departure['trip']['times'][-1]['stop']['atco_code'])

                            try:
                                departure['destination_stop'] =  stops_data[destination_id]
                            except KeyError:
                                print("getting stop metadata from "+'https://bustimes.org/api/stops/'+str(destination_id)+'/?format=json')
                                departure['destination_stop'] = json.loads(requests.get('https://bustimes.org/api/stops/'+str(destination_id)+'/?format=json', headers=headers, timeout=10).text)
                                stops_data[destination_id] = departure['destination_stop']

                            #Destination Filter
                            try:
                                if info['extras']['filter']['key'] == 'destination_stop/atco_code':
                                    #print(info['extras']['filter']['key'])
                                    if info['extras']['filter']['type'] == 'is_not':
                                        #print(info['extras']['filter']['type'])
                                        if departure['destination_stop']['atco_code'] in info['extras']['filter']['value']:
                                            #print(departure['destination_stop']['atco_code'], info['extras']['filter']['value'])
                                            continue
                            except KeyError:
                                pass

                            departure['display']['destination'] = departure['destination_stop']['name'].replace(' '+departure['destination_stop']['common_name'],', '+departure['destination_stop']['common_name']).replace(' Town Ctr','')
                            departure['display']['via'] = None
                            departure['display']['notes'] = None
                            departure['page_expected'] = None

                            try:
                                if table_headers[2] == 'Ex\xadpected':
                                    departure['page_expected'] = l.findAll('td')[3].text.strip()
                                    try:
                                        if table_headers[3] == 'Bay':
                                            departure['stop']['bay'] = l.findAll('td')[4].text.strip()
                                    except IndexError:
                                        pass
                                elif table_headers[2] == 'Bay':
                                    departure['stop']['bay'] = l.findAll('td')[3].text.strip()
                            except IndexError:
                                pass

                            if datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_scheduled'],'%x %H:%M').astimezone() > nowLocal():
                                departure['page_scheduled_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_scheduled'],'%x %H:%M').astimezone()
                            elif datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_scheduled'],'%x %H:%M').astimezone() > nowLocal()-datetime.timedelta(hours=12):
                                departure['page_scheduled_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_scheduled'],'%x %H:%M').astimezone()
                            else:
                                departure['page_scheduled_dt'] = datetime.datetime.strptime((nowLocal()+datetime.timedelta(days=1)).strftime('%x ')+departure['page_scheduled'],'%x %H:%M').astimezone()
                            try:
                                if datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_expected'],'%x %H:%M').astimezone() > nowLocal():
                                    departure['page_expected_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_expected'],'%x %H:%M').astimezone()
                                elif datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_expected'],'%x %H:%M').astimezone() > nowLocal()-datetime.timedelta(hours=12):
                                    departure['page_expected_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+departure['page_expected'],'%x %H:%M').astimezone()
                                else:
                                    departure['page_expected_dt'] = datetime.datetime.strptime((nowLocal()+datetime.timedelta(days=1)).strftime('%x ')+departure['page_expected'],'%x %H:%M').astimezone()
                            except (TypeError, KeyError, ValueError):
                                departure['page_expected_dt'] = departure['page_scheduled_dt']

                            timing_points_list = list(filter(lambda d: d['timing_status'] in ['PTP'], departure['trip']['times']))
                            timing_points_data = {}

                            if timing_points_list[0]['stop']['atco_code'] == timing_points_list[-1]['stop']['atco_code']:
                                departure['circular'] = True
                            else:
                                departure['circuar'] = None

                            for i in timing_points_list:
                                try:
                                    timing_points_data[i['stop']['atco_code']] = stops_data[i['stop']['atco_code']]
                                except KeyError:
                                    print("getting data from "+'https://bustimes.org/api/stops/'+str(i['stop']['atco_code'])+'/?format=json')
                                    stops_data[i['stop']['atco_code']] = json.loads(requests.get('https://bustimes.org/api/stops/'+str(i['stop']['atco_code'])+'/?format=json', headers=headers, timeout=10).text)
                                    timing_points_data[i['stop']['atco_code']] = stops_data[i['stop']['atco_code']]

                            departure['timing_points_data'] = timing_points_data
                            via_calc = []

                            for tp_stop, tp_info in departure['timing_points_data'].items():
                                tp = {}
                                for i in departure['trip']['times']:
                                    try:
                                        if i['stop']['atco_code'] == tp_info['atco_code']:
                                            tp = i
                                            #break
                                    except KeyError:
                                        pass
                                try:
                                    if datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_departure_time'],'%x %H:%M').astimezone() > nowLocal():
                                        tp['aimed_departure_time_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_departure_time'],'%x %H:%M').astimezone()
                                    elif datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_departure_time'],'%x %H:%M').astimezone() > nowLocal()-datetime.timedelta(hours=12):
                                        tp['aimed_departure_time_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_departure_time'],'%x %H:%M').astimezone()
                                    else:
                                        tp['aimed_departure_time_dt'] = datetime.datetime.strptime((nowLocal()+datetime.timedelta(days=1)).strftime('%x ')+tp['aimed_departure_time'],'%x %H:%M').astimezone()

                                    if tp['aimed_departure_time_dt'] >= departure['page_scheduled_dt']:
                                        via_calc.append({'atco_code':tp_info['atco_code'],'common_name':tp_info['common_name'],'name':tp_info['name'],'time_dt':tp['aimed_departure_time_dt']})

                                except TypeError:
                                    if datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_arrival_time'],'%x %H:%M').astimezone() > nowLocal():
                                        tp['aimed_arrival_time_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_arrival_time'],'%x %H:%M').astimezone()
                                    elif datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_arrival_time'],'%x %H:%M').astimezone() > nowLocal()-datetime.timedelta(hours=12):
                                        tp['aimed_arrival_time_dt'] = datetime.datetime.strptime(nowLocal().strftime('%x ')+tp['aimed_arrival_time'],'%x %H:%M').astimezone()
                                    else:
                                        tp['aimed_arrival_time_dt'] = datetime.datetime.strptime((nowLocal()+datetime.timedelta(days=1)).strftime('%x ')+tp['aimed_arrival_time'],'%x %H:%M').astimezone()

                                    if tp['aimed_arrival_time_dt'] >= departure['page_scheduled_dt']:
                                        via_calc.append({'atco_code':tp_info['atco_code'],'common_name':tp_info['common_name'],'name':tp_info['name'],'time_dt':tp['aimed_arrival_time_dt']})

                                except KeyError:
                                    pass

                            via_calc = sorted(via_calc, key=lambda x: (x['time_dt']))
                            via_calc = via_calc[:-1]
                            via_atco = []
                            for i in via_calc:
                                via_atco.append(i['atco_code'])
                            departure['via_atco'] = via_atco
                            via_text = ''

                            for i in via_calc:
                                if i == via_calc[-1]:
                                    via_text+=' & '+i['common_name']
                                elif i == via_calc[-2]:
                                    via_text+=i['common_name']
                                else:
                                    via_text+=i['common_name']+', '
                            #print(via_text)


                            if '8-derby-mackworth' in departure['page_service']['slug']:
                                departure['display']['destination'] = 'Mackworth Estate, Henley Green'
                                departure['display']['via'] = 'Slack Lane'
                            elif 'ta-derby-allestree' in departure['page_service']['slug']:
                                departure['service']['line_name'] = 'The Allestree'
                                if via_atco == ['109000009153', '109000008741', '109000008787', '109000008732', '109000009152']:
                                    departure['display']['destination'] = 'Allestree'
                                    departure['display']['via'] = 'University, then the Green Route'
                                elif via_atco == ['109000009153', '109000008741', '109000008792', '109000008787', '109000008732', '109000009152']:
                                    departure['display']['destination'] = 'Allestree, Woodlands Top'
                                    departure['display']['via'] = 'University, then the Green Route'
                                elif via_atco == ['109000009153', '109000008731', '109000008788', '109000008742', '109000009152']:
                                    departure['display']['destination'] = 'Allestree'
                                    departure['display']['via'] = 'University, then the Blue Route'
                                elif via_atco == ['109000009153', '109000008731', '109000008788', '109000008791', '109000008742', '109000009152']:
                                    departure['display']['destination'] = 'Allestree, Woodlands Top'
                                    departure['display']['via'] = 'University, then the Blue Route'
                            elif 'tm-derby-mickleover' in departure['page_service']['slug']:
                                departure['service']['line_name'] = 'The Mickleover'
                                if via_atco == ['109000009011', '109000008906', '109000008931', '109000008939', '109000009012']:
                                    departure['display']['destination'] = 'Mickleover'
                                    departure['display']['via'] = 'Royal Derby Hospital, then the Green Route'
                                elif via_atco == ['109000009011', '109000008938', '109000008930', '109000008903', '109000009012']:
                                    departure['display']['destination'] = 'Mickleover'
                                    departure['display']['via'] = 'Royal Derby Hospital, then the Blue Route'

                            elif 'sky-skylink-derby-leicester-loughborough-east-midl' in departure['page_service']['slug']:
                                if departure['destination_stop']['atco_code'] in ['269030091']:
                                    departure['display']['via'] = 'East Mids Airport & Loughborough'
                                elif departure['destination_stop']['atco_code'] in ['260007333','260007201']:
                                    departure['display']['via'] = 'East Mids Airport'

                            elif via_atco == [ "1090BSTN23","1000DOOL4017","1000DBWL4005", "1000DBGA4002","1000DBLC3994","100000022178","1000DMTS1132","1000DDMR3919","109000008802" ]:
                                departure['display']['destination'] = 'Belper Estates fast'
                                departure['display']['via'] = 'A38 to Kilburn Toll Bar'
                                departure['display']['notes'] = 'Returns to Derby as 6.4 via Duffield'

                            elif via_atco == ["109000008733","1000DQCR5878", "1000DKKR5663","1000DWUB5665","1000DCOH5839","1000DHWAR708", "1000DBAR5814","1000DAPA4644"]:
                                departure['display']['via'] = 'Quarndon & Hulland Ward'
                            elif via_atco == ["1090BSTN23", "1000DOOL4017", "1000DBWL4005","1000DBGA4002","1000DBLC3994"]:
                                departure['display']['via'] = 'A38 & Belper Estates'
                            elif via_atco == [ "109000022165", "1090DDAR1606", "1000DLEB4088","1000DCAR1608", "1000DHTS1676","1000DBSB4119","1000DOSL1819","1000DBKR4038" ]:
                                departure['display']['via'] = 'Little Eaton & Holbrook'

                            elif via_atco == ["1090BSTN25","43000105509","490008016CS","490016736W", "450032500"]:
                                departure['display']['via'] = 'Birmingham Airport and Heathrow Central'
                            elif via_atco == (["1090BSTN25","3390UN04","3390BB10","269030094","049000000804","02900033","02900065","490008016CS","49001643011","4400CY0375"] or ["1090BSTN25","3390UN04","3390BB10","269030094","049000000804","02900033","02900065","490008016CS","49001643011","4400CY0375"]):
                                departure['display']['via'] = 'Milton Keynes Coachway, Luton Airport & Heathrow Airport'
                            elif via_atco == ["1090BSTN25","1000DCBSB267","370010217","370010201","450027815","450032500" ]:
                                departure['display']['via'] = 'Sheffield & Leeds'
                            elif via_atco ==  [ "1090BSTN25", "269030094","269046004","490000082C","49000144CSZ"] :
                                departure['display']['via'] = 'Finchley Road'
                            elif via_atco == [ "1090BSTN25", "3390UN04", "3390BB10","269030094", "049000000804", "02900033","02900065", "490008016CS","490000104WH"]:
                                departure['display']['via'] = 'Milton Keynes Coachway & Luton Airport'

                            #else:
                                #departure['display']['via'] = via_text


                            if departure['page_service']['slug'] == 'v1-derby-etwall-hilton-hatton-tutbury-rolleston-2' and departure['destination_stop']['atco_code'] in ['3800C302701','3800C303200','3800C303900']:
                                departure['display']['via'] = 'Tutbury'
                            elif departure['page_service']['slug'] == 'v3-derby-littleover-findern-willington-repton-ne-3' and departure['destination_stop']['atco_code'] in ['3800C302700']:
                                departure['display']['via'] = 'Willington'
                            if departure['destination_stop']['atco_code'] in ['49001643011']:
                                departure['display']['destination'] = 'Heathrow Airport, Terminal 5'
                            elif departure['destination_stop']['atco_code'] in ['490016736W']:
                                departure['display']['destination'] = 'London Victoria, Coach Station'


                            departures_full_data.append(departure)

                        except Exception as e: # <--- NEW INNER EXCEPT BLOCK
                            print(f"Error processing departure row for stop {stop}: {e}")
                            print(traceback.format_exc()) # <--- Log the full traceback for this row
                            continue
        except Exception as e: # <--- REPLACE YOUR 'except AttributeError:' with this.
            print(f"General scraping error for stop {stop}: {e}")
            print(traceback.format_exc()) # <--- THIS IS THE NEW IMPORTANT LINE
    #print(json.dumps(stops_request_data, indent=4))
    #print(json.dumps(departures_full_data, indent=4))

    for d in departures_full_data:
        departure = {
            'stop' : {'indicator':d['stop']['indicator'],'icon':d['stop']['icon'],'bay':d['stop']['bay']},
            'service' : d['page_service']['line_name'],
            'destination' : d['display']['destination'],
            'via': d['display']['via'],
            'notes': d['display']['notes'],
            'scheduled' : d['page_scheduled'],
            'scheduled_dt' : d['page_scheduled_dt'],
            'expected' : d['page_expected'],
            'operator' : d['trip']['operator']['name'],
            'expected_dt': d['page_expected_dt'],
            'debug': ''#d['page_trip_id']

        }
        departures_summary.append(departure)
    departures_summary = sorted(departures_summary, key=lambda x: (x['expected_dt']))

    with open('_data/departures full.json',"w", encoding="utf-8") as f:
        f.write(json.dumps(departures_full_data, indent=4, default=str))

    with open('_data/departures sumary.json',"w", encoding="utf-8") as f:
        f.write(json.dumps(departures_summary, indent=4, sort_keys=True, default=str))

    with open('_data/stops.json',"w", encoding="utf-8") as f:
        f.write(json.dumps(stops_data, indent=4, default=str))

    with open('_data/trips.json',"w", encoding="utf-8") as f:
        f.write(json.dumps(trips_data, indent=4, default=str))

    return departures_summary

def printDepartures(limit=15, request = None ):
    """prints departures in an easy to read table"""
    if request is None:
        request = normal_stops

    departures = get_departures(request)
    print("-"*128)
    print("| STOP | SERVICE |                                                    DESTINATION |  SCH  |  EST  |                   OPERATOR |")
    print("-"*128)

    for x in range(limit):
        try:
            i = departures[x]
        except IndexError:
            break
        print("| %5s | %6s | %62s | %5s | %5s | %26s | %1s" %(i['stop']['icon'] or i['stop']['indicator'] or i['stop']['bay'], i['service'], i['destination'], i['scheduled'], i['expected'] or '', i['operator'], i['debug']))
        if i['via'] != None:
            print("| %5s | %6s | %62s | %5s | %5s | %26s |" %( '', '', 'via '+i['via'], '', '', ''))
        if i['notes'] != None:
            print("| %5s | %6s | %62s | %5s | %5s | %26s |" %( '', '', i['notes'], '', '', ''))
        print("| %5s | %6s | %62s | %5s | %5s | %26s |" %( '', '', '', '', '', ''))
    print("-"*128)
    print('%127s' %('Data From bustimes.org - Last Updated '+str(nowLocal().strftime('%Y-%m-%d %X'))))

@app.route('/')
def hello_flask():
    """api test"""
    return "Hello from Flask!"

@app.route('/departures')
def get_bus_departures_api():
    """pass departures data to api"""
    try:
        departures_data = get_departures(normal_stops)
        return jsonify(departures_data)
    except Exception as e:
        print(f"Error fetching departures: {e}")
        print(traceback.format_exc()) # Keep this for your file logs via print

        # --- NEW: DIRECTLY PRINT TRACEBACK TO STDOUT FOR DEBUGGING ---
        print(f"--- TRACEBACK FOR /departures ERROR (Direct Print) ---")
        print(traceback.format_exc())
        print(f"--------------------------------------------------")
        # --- END NEW ---

        return jsonify({"error": str(e), "message": "Could not fetch departures"}), 500


if __name__ == '__main__':
    # Ensure this is False and port is 8000
    app.run(host='0.0.0.0', port=8000, debug=False)

#bus_station_request
#while True:
#printDepartures(limit=17) # Commented out
#printDepartures(request = bus_station_request, limit = 10) # Commented out
#
#    time.sleep(300)