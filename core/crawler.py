import requests
from bs4 import BeautifulSoup
import json


def login(username, password):
    # return None if the login fails
    # return an instance of requests.Session() if the login succeeds

    with requests.session() as s:
        data = {
            'si_id': username,
            'si_pwd': password
        }
        res = s.post('https://sso.snu.ac.kr/safeidentity/modules/auth_idpwd', data=data)
        soup = BeautifulSoup(res.text, 'html5lib')
        try:
            data = {i['name']: i['value'] for i in soup.find('form').find_all('input')}
        except AttributeError:
            return None
        res = s.post('https://sso.snu.ac.kr/nls3/fcs', data=data)
        soup = BeautifulSoup(res.text, 'html5lib')
        fonts = soup.find_all('font')
        if len(fonts) == 2:
            res_code = fonts[1].text.strip()
            if res_code == '5402':
                return None
            elif res_code != '2800':
                return None

        s.get('https://shine.snu.ac.kr/com/ssoLoginForSWAction.action')
        return s


def crawl_mysnu(username, password):
    session = login(username, password)
    if session is None:
        return None
    with session as s:
        url = 'https://shine.snu.ac.kr/uni/uni/scor/mrtr/findTabCumlMrksYyShtmClsfTtInq02.action'
        params = {'cscLocale': 'ko_KR', 'strPgmCd': 'S030302'}
        headers = {'Content-Type': 'application/extJs+sua; charset=UTF-8'}
        payload = {
            "SUN": {
                "strSchyy": "2015",
                "strShtmFg": "U000200001",
                "strDetaShtmFg": "U000300001",
                "strBdegrSystemFg": "U000100001",
                "strFlag": "all"
            }
        }
        grade_response = s.post(url, params=params, headers=headers, data=json.dumps(payload))
        grade_response.raise_for_status()
        grade_list = grade_response.json()['GRD_SCOR401']

        semester_name = {
            'U000200001U000300001': '1',
            'U000200001U000300002': 'S',
            'U000200002U000300001': '2',
            'U000200002U000300002': 'W',
        }

        def refine(raw):
            return {
                'year': int(raw['schyy']),
                'semester': semester_name[raw['shtmFg'] + raw['detaShtmFg']],
                'code': raw['sbjtCd'],
                'number': raw['ltNo'],
                'title': raw['sbjtNm'],
                'credit': raw['acqPnt'],
                'grade': raw['mrksGrdCd'],
                'category': raw['cptnSubmattFgCdNm']
            }

    credit_info = [refine(raw) for raw in grade_list]

    with session as s:
        url = 'https://shine.snu.ac.kr/uni/uni/port/stup/findMyMjInfo.action'
        params = {'cscLocale': 'ko_KR', 'strPgmCd': 'S010101'}
        headers = {'Content-Type': 'application/extJs+sua; charset=UTF-8'}
        res = s.post(url, params=params, headers=headers)

    major_info = res.json()['GRD_SREG524']

    return {
        'major_info': major_info,
        'credit_info': credit_info,
    }
