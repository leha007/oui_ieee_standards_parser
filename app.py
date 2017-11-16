import hashlib
import logging
import os
import re
import urllib.request
from os import path
from time import gmtime, strftime

from company import Company

g_hex_splitter = '(hex)'
g_base_splitter = '(base 16)'
g_the_great_dic = {}
g_the_not_so_great_dic = {}

g_tmp_dir = 'tmp'
g_unity_file = 'unity'
g_unity_file_old = 'unity_old'
g_result_file = 'result.csv'
g_updated_file = 'updated.txt'
g_url_http_tag = 'http://'
last_update_file = 'last_update'

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


def renew_files():
    yes_no = 0
    skip = 0
    file_path = os.path.join(g_tmp_dir, last_update_file)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf8') as file:
            print('Standards were downloaded at ' + file.read())
            file.close()
        yes_no = int(input('Do you want renew standards? 1-Yes, 0-No: '))
        if yes_no:
            dir_files = [f for f in os.listdir(g_tmp_dir) if path.isfile(os.path.join(g_tmp_dir, f))]
            for file_name in dir_files:
                if file_name == g_unity_file:
                    if os.path.exists(os.path.join(g_tmp_dir, g_unity_file_old)):
                        os.remove(os.path.join(g_tmp_dir, g_unity_file_old))
                    os.rename(os.path.join(g_tmp_dir, file_name), os.path.join(g_tmp_dir, g_unity_file_old))
                    skip = 1
                elif skip == 1 and file_name == g_unity_file_old:
                    continue
                else:
                    os.remove(os.path.join(g_tmp_dir, file_name))
    return yes_no


def download_files():
    for url_addr in g_file_url_list:
        url_hash = hashlib.md5(url_addr.encode())
        file_path = os.path.join(g_tmp_dir, url_hash.hexdigest())

        if os.path.exists(file_path):
            logging.info('file [' + file_path + ' exist, skip to next url')
            continue

        try:
            logging.info('download [' + url_addr + '] file...')
            urllib.request.urlretrieve(url_addr, file_path)
            logging.info('finished downloading [' + url_addr + '] file successfully')
            file_path = os.path.join(g_tmp_dir, last_update_file)
            if os.path.exists(file_path):
                os.remove(file_path)
            with open(file_path, 'w', encoding='utf8') as wfile:
                wfile.write(strftime("%d/%m/%Y_%H:%M", gmtime()) + '\n')
        except:
            logging.error('unable to retrieve [' + url_addr + '] file')
            pass


def find_url(file_name):
    for url_addr in g_file_url_list:
        if file_name == hashlib.md5(url_addr.encode()).hexdigest():
            return url_addr


def untite_text_files():
    dir_files = [f for f in os.listdir(g_tmp_dir) if path.isfile(os.path.join(g_tmp_dir, f))]
    with open(os.path.join(g_tmp_dir, g_unity_file), 'w', encoding='utf8') as outfile:
        for file_name in dir_files:
            if file_name == g_unity_file or last_update_file == file_name or file_name == g_unity_file_old:
                logging.info('skip result and last updated files ...')
                continue

            logging.info('add [' + file_name + '] file to ' + g_unity_file)
            with open(os.path.join(g_tmp_dir, file_name), 'r', encoding='utf8') as infile:
                outfile.write(find_url(file_name).rstrip())
                outfile.write('\n')
                outfile.write(infile.read())


def add_hex_to_dic(input_dic, line, current_file):
    splitted_line = line.split(g_hex_splitter)
    mac = re.sub('\s+', ' ', splitted_line[0])
    comp = re.sub('\s+', ' ', splitted_line[1])
    if comp not in input_dic:
        input_dic[comp] = Company(comp)

    if current_file not in input_dic[comp].files:
        input_dic[comp].files.append(current_file)
        if input_dic[comp].first_entry:
            input_dic[comp].files_cnt.append(input_dic[comp].files_cnt_tmp)
            input_dic[comp].files_cnt_tmp = 0
    input_dic[comp].first_entry = 1
    input_dic[comp].files_cnt_tmp += 1
    input_dic[comp].add_hex_mac(mac)


def write_last_cnt(input_dic):
    for key, value in input_dic.items():
        input_dic[key].files_cnt.append(input_dic[key].files_cnt_tmp)


def add_base_to_dic(input_dic, line):
    splitted_line = line.split(g_base_splitter)
    mac = re.sub('\s+', ' ', splitted_line[0])
    comp = re.sub('\s+', ' ', splitted_line[1])
    if comp not in input_dic:
        input_dic[comp] = Company(comp)
    input_dic[comp].add_base_mac(mac)


def parse_raw_data_to_something_cool(input_file):
    raw_file = os.path.join(g_tmp_dir, input_file)

    if input_file == g_unity_file:
        input_dic = g_the_great_dic
    else:
        input_dic = g_the_not_so_great_dic

    if not os.path.exists(raw_file):
        logging.error('raw file not found...')
        return

    logging.info('parse raw [' + raw_file + '] file')

    with open(raw_file, 'r', encoding='utf8') as rfile:
        for line in rfile:
            if g_url_http_tag in line:
                current_file = line.rstrip()
            if g_hex_splitter in line:
                add_hex_to_dic(input_dic, line, current_file)
            if g_base_splitter in line:
                add_base_to_dic(input_dic, line)
        write_last_cnt(input_dic)


def compare_dicts_and_write_results():
    logging.info('Comparing dictionaries for Hachipuri... ')
    if os.path.exists(g_updated_file):
        os.remove(g_updated_file)
    # Here won't be Pushkin's dictionaries compare logic
    with open(g_updated_file, 'w', encoding='utf8') as wfile:
        wfile.write('Added:' + '\n')
        for key, value in g_the_great_dic.items():
            if key not in g_the_not_so_great_dic:
                line_to_write = 'Company: ' + str(key) + ' Added to files: ' + ', '.join(
                    str(line) for line in value.files) + '; ' + ', '.join(
                    str(line) for line in value.hrdw_addr_array)
                wfile.write(line_to_write + '\n')
            else:
                ind1 = 0
                for address_ind, address in enumerate(value.files):
                    if address not in g_the_not_so_great_dic[key].files:
                        line_to_write = 'Company: ' + str(key) + ' Added to file: ' + str(address) + '; ' \
                                        + ', '.join(str(line) for line in value.hrdw_addr_array)
                        wfile.write(line_to_write + '\n')
                    else:
                        for ind2 in range(0, value.files_cnt[address_ind]):
                            if value.hrdw_addr_array[ind1] not in g_the_not_so_great_dic[key].hrdw_addr_array:
                                line_to_write = 'Company: ' + str(key) + ' Added to file: ' + str(address) + '; ' \
                                                + str(value.hrdw_addr_array[ind1])
                                wfile.write(line_to_write + '\n')
                            ind1 += 1

        wfile.write('Removed:' + '\n')
        for key, value in g_the_not_so_great_dic.items():
            if key not in g_the_great_dic:
                line_to_write = 'Company: ' + str(key) + ' Removed from files: ' + ', '.join(
                    str(line) for line in value.files) + '; ' + ', '.join(
                    str(line) for line in value.hrdw_addr_array)
                wfile.write(line_to_write + '\n')
            else:
                ind1 = 0
                for address_ind, address in enumerate(value.files):
                    if address not in g_the_great_dic[key].files:
                        line_to_write = 'Company: ' + str(key) + ' Removed from file: ' + str(address) + '; ' \
                                        + ', '.join(str(line) for line in value.hrdw_addr_array)
                        wfile.write(line_to_write + '\n')
                    else:
                        for ind2 in range(0, value.files_cnt[address_ind]):
                            if value.hrdw_addr_array[ind1] not in g_the_great_dic[key].hrdw_addr_array:
                                line_to_write = 'Company: ' + str(key) + ' Removed from file: ' + str(address) + '; ' \
                                                + str(value.hrdw_addr_array[ind1])
                                wfile.write(line_to_write + '\n')
                            ind1 += 1


def save_parsed_data_to_file():
    logging.info('number of companies in dictionary: ' + str(len(g_the_great_dic)))
    headers = 'Company_Names;Occurrence_Counter;URL;MAC_Ranges'

    with open(g_result_file, 'w', encoding='utf8') as wfile:
        wfile.write(headers + '\n')
        for key, value in g_the_great_dic.items():
            if value.cnt > 1:
                line_to_write = value.name + ';' + str(value.cnt) + ';' + ','.join(
                    str(line) for line in value.files) + ';' + ','.join(
                    str(line) for line in value.files_cnt) + ';' + ','.join(
                    str(line) for line in value.hrdw_addr_array)
                wfile.write(line_to_write + '\n')


def main():
    try:
        logging.info('check if needed directories exist')
        verify_dir()

        logging.info('check if needed new standards Kutigeski Djaleap')
        renew = renew_files()

        logging.info('download files...')
        download_files()

        logging.info('unite downloaded files, Timur Haivon')
        untite_text_files()

        logging.info('parse data')
        parse_raw_data_to_something_cool(g_unity_file)

        if renew:
            parse_raw_data_to_something_cool(g_unity_file_old)
            compare_dicts_and_write_results()

        logging.info('save parsed data to [' + g_result_file + '] file')
        save_parsed_data_to_file()
    except:
        logging.error("general error Djaleap...")


if __name__ == "__main__":
    config_logging()
    logging.info('run oui-ieee-standards parser')
    main()
    logging.info('parser finished')
