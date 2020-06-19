import subprocess
import re
import requests
import argparse


def input_data():
    parser = argparse.ArgumentParser(description="Запуск производится из консоли с ключом --description где нужно вставить ip адрес или доменное имя"
                    "\nРезультат работы программы будет выведен в консоли"
                    "\nПример запуска: python main.py --description e1.ru")
    parser.add_argument('--destination', type=str, help="Введите IP адрес или доменное имя")
    namespace = parser.parse_args()
    if namespace.destination is not None:
        return namespace.destination
    else:
        raise Exception("Введите IP адрес или доменное имя с помощью --destination")


def tracert(destination):
    cmd = 'tracert ' + destination
    output = subprocess.check_output(cmd, universal_newlines=True, encoding="cp866")

    addresses = output.split("\n")[4:-2]
    ip_addresses = {a: None for a in range(len(addresses))}

    for address in addresses:
        if address != "":
            address.strip()
            res = address.split()
            number, ip = int(res[0].strip()), res[-1].strip().replace("]", '').replace("[", "")
            if re.search(r'([0-9]\.)+', ip) is not None:
                ip_addresses[number] = ip

    table = ""
    for key in list(ip_addresses.keys()):
        if ip_addresses[key] is not None:
            AS = get_as(ip_addresses[key])
            table += str(key) + "\t" + str(ip_addresses[key]) + "\t\t" + AS + "\n"
    print(table)


def get_html(ip):
    try:
        result = requests.get("https://www.tendence.ru/tools/whois/a.s." + ip)
        result.raise_for_status()
        return result.text
    except (requests.RequestException, ValueError):
        print("ServerError")
        SystemExit(0)


def get_as(ip):
    text = get_html(ip)
    ap_pattern = re.compile(r"<br>Автономная система:(\w)*?")
    res = re.search(ap_pattern, text)
    if res is not None:
        country_pos = re.search(r"Страна", text)
        provider_pos = re.search(r"mnt-by", text)
        AS = text[res.end() + 9:res.end() + 20]
        end = AS.find('<')
        if country_pos is not None and provider_pos is not None:
            country = "".join(re.findall('[A-Z]', text[country_pos.end():country_pos.end() + 15]))
            end_of_provider = re.search(r"<br>",
                                        text[provider_pos.end():provider_pos.end() + 40]).start() + provider_pos.end()
            provider = text[provider_pos.end():end_of_provider].replace(" ", "").replace(":", "")
            return str(AS[:end]) + '\t' + str(country) + '\t' + str(provider)
        return str(AS[:end]) + "\t-\t-"
    return ""


if __name__ == "__main__":
    destination = input_data()
    tracert(destination)
