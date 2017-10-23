import hashlib
import logging
import os
import re
import urllib.request
from os import path

from company import Company

g_hex_splitter = '(hex)'
g_base_splitter = '(base 16)'
g_the_great_dic = {}

g_tmp_dir = 'tmp'
g_unity_file = 'unity'
g_result_file = 'result.csv'

g_file_url_list = ['http://standards-oui.ieee.org/oui/oui.txt',
                   'http://standards-oui.ieee.org/oui28/mam.txt',
                   'http://standards-oui.ieee.org/oui36/oui36.txt',
                   'http://standards-oui.ieee.org/iab/iab.txt']


def config_logging():
    logging.basicConfig(level=logging.INFO)


def verify_dir():
    if not os.path.isdir(g_tmp_dir):
        logging.info('directory ' + g_tmp_dir + ' not exist..., lets create one')
        os.makedirs(g_tmp_dir)
    else:
        logging.info(g_tmp_dir + ' directory exist')


def download_files():
    for url_addr in g_file_url_list:
        url_hash = hashlib.md5(url_addr.encode())
        file_path = g_tmp_dir + '/' + url_hash.hexdigest()

        if os.path.exists(file_path):
            logging.info('file [' + file_path + ' exist, skip to next url')
            continue

        try:
            logging.info('download [' + url_addr + '] file...')
            urllib.request.urlretrieve(url_addr, file_path)
            logging.info('finished downloading [' + url_addr + '] file successfully')
        except:
            logging.error('unable to retrieve [' + url_addr + '] file')
            pass


def untite_text_files():
    dir_files = [f for f in os.listdir(g_tmp_dir) if path.isfile(os.path.join(g_tmp_dir, f))]
    with open(os.path.join(g_tmp_dir, g_unity_file), 'w', encoding='utf8') as outfile:
        for file_name in dir_files:
            if file_name == g_unity_file:
                logging.info('skip result file...')
                continue

            logging.info('add [' + file_name + '] file to ' + g_unity_file)
            with open(os.path.join(g_tmp_dir, file_name), 'r', encoding='utf8') as infile:
                outfile.write(infile.read())


def get_raw_file():
    return os.path.join(g_tmp_dir, g_unity_file)


def add_hex_to_dic(line):
    splitted_line = line.split(g_hex_splitter)
    mac = re.sub('\s+', ' ', splitted_line[0])
    comp = re.sub('\s+', ' ', splitted_line[1])
    if comp not in g_the_great_dic:
        g_the_great_dic[comp] = Company(comp)

    g_the_great_dic[comp].add_hex_mac(mac)


def add_base_to_dic(line):
    splitted_line = line.split(g_base_splitter)
    mac = re.sub('\s+', ' ', splitted_line[0])
    comp = re.sub('\s+', ' ', splitted_line[1])

    if comp not in g_the_great_dic:
        g_the_great_dic[comp] = Company(comp)

    g_the_great_dic[comp].add_base_mac(mac)


def parse_raw_data_to_something_cool():
    raw_file = get_raw_file()

    if not os.path.exists(raw_file):
        logging.error('raw file not found...')
        return

    logging.info('parse raw [' + raw_file + '] file')

    with open(raw_file, 'r', encoding='utf8') as rfile:
        for line in rfile:
            if g_hex_splitter in line:
                add_hex_to_dic(line)
            if g_base_splitter in line:
                add_base_to_dic(line)


def save_parsed_data_to_file():
    logging.info('Number of companies in dictionary: ' + str(len(g_the_great_dic)))
    headers = 'Company_Names;Occurrence_Counter;MAC_Ranges'

    with open(g_result_file, 'w', encoding='utf8') as wfile:
        wfile.write(headers + '\n')
        for key, value in g_the_great_dic.items():
            if value.cnt > 1:
                line_to_write = value.name + ';' + str(value.cnt) + ';' + ','.join(
                    str(line) for line in value.hrdw_addr_array)
                wfile.write(line_to_write + '\n')


def main():
    try:
        logging.info('check if needed directories exist')
        verify_dir()

        logging.info('download files...')
        download_files()

        logging.info('unite downloaded files')
        untite_text_files()

        logging.info('parse data')
        parse_raw_data_to_something_cool()

        logging.info('save parsed data to [' + g_result_file + '] file')
        save_parsed_data_to_file()
    except:
        logging.error("general error...")


if __name__ == "__main__":
    config_logging()
    logging.info('run oui-ieee-standards parser')
    main()
    logging.info('parser finished')
