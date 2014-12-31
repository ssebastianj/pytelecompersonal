#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import logging
import requests
import sys
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

# ----------------------------------------------------------------------------
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if not PY2:
    text_type = str
    string_types = (str,)
    unichr = chr
    inp = input

    def b(s):
        return s.encode("utf-8")

    def u(s):
        return s

    def a(s):
        return s
else:
    text_type = unicode
    string_types = (str, unicode)
    unichr = unichr
    inp = raw_input

    def b(s):
        return s

    def u(s):
        return unicode(s, "unicode_escape")

    def a(s):
        return s.encode('ascii', 'ignore')
# ----------------------------------------------------------------------------

# Logging Config
logging.basicConfig(level=logging.DEBUG,
                    format="[%(levelname)s] : %(message)s")


def get_line_info(cod_area, nro_linea, clave_personal):
    cod_area = cod_area.strip()
    nro_linea = nro_linea.strip()
    password = clave_personal.strip()

    if not cod_area.isdigit() or not nro_linea.isdigit() or not password.isdigit():
        raise ValueError

    # Define browser headers
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Referer': 'https://autogestion.personal.com.ar/individuos/',
               'Accept-Encoding': 'gzip,deflate,sdch',
               'Accept-Language': 'es-ar,es;q=0.8,en-us;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'Host': 'autogestion.personal.com.ar',
               }

    # Get ASP.NET __VIEWSTATE and __EVENTVALIDATION values
    tc_session = requests.Session()
    tc_session.mount('http://', HTTPAdapter(max_retries=255))
    tc_session.mount('https://', HTTPAdapter(max_retries=255))

    response = None
    try:
        response = tc_session.get('https://autogestion.personal.com.ar/individuos/Index.aspx',
                                  headers=headers,
                                  allow_redirects=False,
                                  stream=False)
    except (requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout) as e:
        print(e)

    if response is not None:
        soup = BeautifulSoup(response.content)
        viewstate = soup.select('#__VIEWSTATE')[0]['value']
        eventvalidation = soup.select('#__EVENTVALIDATION')[0]['value']

        logging.debug(viewstate)
        logging.debug(eventvalidation)

        # Build POST params
        login_data = {r'ctl00$LogueoPropio$TxtArea': cod_area,
                      r'ctl00$LogueoPropio$TxtLinea': nro_linea,
                      r'ctl00$LogueoPropio$TxtPin': password,
                      r'TxtArea': cod_area,
                      r'TxtLinea': nro_linea,
                      r'TxtPin': password,
                      r'IDToken1': cod_area + nro_linea,
                      r'IDToken2': password,
                      r'IDToken3': '',
                      r'goto': 'https://autogestion.personal.com.ar/Individuos/default.aspx',
                      r'gotoOnFail': 'https://autogestion.personal.com.ar/Individuos/Respuesta.aspx',
                      r'realm': '/servicios',
                      r'__EVENTVALIDATION': eventvalidation,
                      r'__LASTFOCUS': '',
                      r'__EVENTTARGET': '',
                      r'__EVENTARGUMENT': '',
                      r'__VIEWSTATE': viewstate,
                      r'buscar': ''
                      }

        # Redefine browser headers
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   #'Referer': 'https://autogestion.personal.com.ar/Individuos/index.aspx',
                   'Accept-Encoding': 'gzip,deflate,sdch',
                   'Accept-Language': 'es-ar,es;q=0.8,en-us;q=0.5,en;q=0.3',
                   'Connection': 'keep-alive',
                   #'Host': 'sso.personal.com.ar',
                   'DNT': '1',
                   #'Origin': 'https://autogestion.personal.com.ar'
                   }

        response = None
        try:
            response = tc_session.post('https://sso.personal.com.ar/openam/UI/Login',
                                       headers=headers,
                                       data=login_data,
                                       allow_redirects=True,
                                       stream=False)
        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            print(e)

    if response is not None:
        logging.debug(response)

        soup = BeautifulSoup(response.content)

        try:
            usuario_id = soup.select('#ctl00_MenuMiCuentaCTL_LbUsuario1')[0].text
        except IndexError:
            usuario_id = ''

        try:
            nro_linea = soup.select('#ctl00_MenuMiCuentaCTL_LbNumeroLinea1')[0].text
        except IndexError:
            nro_linea = ''

        try:
            tipo_plan_id = soup.select('#ctl00_ContenedorAutogestion_lblTipoPlan')[0].text
        except IndexError:
            tipo_plan_id = ''

        try:
            nombre_plan_id = soup.select('#ctl00_ContenedorAutogestion_lblNombrePlan')[0].text
        except IndexError:
            nombre_plan_id = ''

        try:
            estado_linea_id = soup.select('#ctl00_ContenedorAutogestion_lblEstadoLinea')[0].text
        except IndexError:
            estado_linea_id = ''

        try:
            saldo_id = soup.select('#ctl00_ContenedorAutogestion_lblSaldo')[0].text
        except IndexError:
            saldo_id = ''

        try:
            vto_saldo_id = soup.select('#ctl00_ContenedorAutogestion_lblVencimiento2')[0].text
        except IndexError:
            vto_saldo_id = ''

        try:
            puntos_cp_id = soup.select('#ctl00_MenuMiCuentaCTL_LbPuntosClubPersonal')[0].text
        except IndexError:
            puntos_cp_id = ''

        try:
            minutos_libres_consumidos = soup.select('#ctl00_ContenedorAutogestion_lblConsumido')[0].text
        except IndexError:
            minutos_libres_consumidos = ''

        try:
            minutos_libres_total = soup.select('#ctl00_ContenedorAutogestion_lblTotal')[0].text
        except IndexError:
            minutos_libres_total = ''

        info_linea = {'usuario': usuario_id,
                      'nro_linea': nro_linea,
                      'tipo_plan': tipo_plan_id,
                      'nombre_plan': nombre_plan_id,
                      'estado_linea': estado_linea_id,
                      'saldo': saldo_id,
                      'vto_saldo': vto_saldo_id,
                      'puntos_cp': puntos_cp_id,
                      'minutos_libres_total': minutos_libres_total,
                      'minutos_libres_consumidos': minutos_libres_consumidos
                      }

        return info_linea
    else:
        return None


if __name__ == '__main__':
    from getpass import getpass

    cod_area = inp('Codigo de area: (0)')
    nro_linea = inp('Numero de linea: (15)')
    clave_personal = getpass(a('Clave personal: '))

    line_info = get_line_info(cod_area, nro_linea, clave_personal)

    print('\nUsuario: {0}\n'
          'Número de línea: {1}\n'
          'Tipo de plan: {2}\n'
          'Nombre de plan: {3}\n'
          'Estado de línea: {4}\n'
          'Saldo disponible: ${5}\n'
          'Vencimiento del saldo: {6}\n'
          'Total de minutos libres: {7}\n'
          'Minutos libres consumidos: {8}\n'
          'Puntos de Club Personal: {9}\n'.format(line_info['usuario'],
                                                  line_info['nro_linea'],
                                                  line_info['tipo_plan'],
                                                  line_info['nombre_plan'],
                                                  line_info['estado_linea'],
                                                  line_info['saldo'],
                                                  line_info['vto_saldo'],
                                                  line_info['minutos_libres_total'],
                                                  line_info['minutos_libres_consumidos'],
                                                  line_info['puntos_cp']
                                                  ))
