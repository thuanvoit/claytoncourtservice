import requests
from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language':
            'en-US, en;q=0.5'})


class Court(Enum):
    STATE = 'L'
    MAGISTRATE = 'M'
    SUPERIOR = 'U'



def parse_dt(raw_dt):
    try:
        date_format = "%m/%d/%Y"
        datetime.strptime(raw_dt, date_format)
        return True
    except:
        return False


def index_exists(info, index):
    for inf in info['case_info']:
        if index == inf['index']:
            return True
    return False

def request_extractor(case_number, case_type):
    CTT = Court[case_type].value
    CYR = case_number[0:4]
    CTP = case_number[4:6]
    CSQ = case_number[6::]

    URL = f'https://weba.claytoncountyga.gov/casinqcgi-bin/wci205r.pgm?ctt={CTT}&dvt=V&cyr={CYR}&ctp={CTP}&csq={CSQ}'

    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def info_table_extractor(info, data):
    max_index = 0
    case_info = data.find('table').find_all('table')[3]
    case_info_trs = case_info.find_all('tr')

    for j, tr in enumerate(case_info_trs):
        tds = tr.find_all('td')
        if len(tds) < 4:
            continue
        td_date = tds[0].text.strip()
        if (parse_dt(td_date)):
            td_action = tds[2].text.strip()
            td_info = tds[3].text.strip()
            info['case_info'].append({
                'index': j,
                'date': td_date,
                'action': td_action,
                'description': [
                    td_info
                ]
            })
            if j > max_index:
                max_index = j

    for i, inf in enumerate(info['case_info']):
        case_index = inf['index']
        current_index = case_index + 1
        while (current_index != max_index):
            if index_exists(info, current_index):
                break
            current_index_info = case_info_trs[current_index]
            td_info = current_index_info.find_all('td')
            if len(td_info) < 4:
                break
            addition_info = td_info[3].text.strip()
            current_index += 1
            info['case_info'][i]['description'].append(addition_info)
    return info


def case_header_extractor(info, data):
    header = data.find('table').find_all('table')[0]
    header_trs = header.find_all('tr')

    case_number = header_trs[0].find_all('td')[1].text.strip()
    filling_date = header_trs[1].find_all('td')[1].text.strip()
    judge = header_trs[0].find_all('td')[4].text.strip()
    status = [
        header_trs[1].find_all('td')[4].text.strip(),
        header_trs[2].find_all('td')[4].text.strip()
    ]

    info['case_number'] = case_number
    info['judge'] = judge
    info['filling_date'] = filling_date
    info['status'] = status

def case_searcher(case_number, case_type):
    info = {
        'case_number': '',
        'judge': '',
        'filling_date': '',
        'judge': '',
        'status': [],
        'case_info': []
    }

    data = request_extractor(case_number, case_type)
    
    case_header_extractor(info, data)
    info_table_extractor(info, data)

    return info
