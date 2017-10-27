class Company():
    def __init__(self, name):
        self.name = name.strip()
        self.cnt = 0
        self.hex = ''
        self.base = ''
        self.hrdw_addr_array = []
        self.files = []
        self.files_cnt = []
        self.files_cnt_tmp = 0
        self.first_entry = 0

    def add_hex_mac(self, mac):
        self.hex = mac.strip()

    def add_base_mac(self, mac):
        self.base = mac.strip()
        self.trigger()

    def trigger(self):
        if self.hex != '' and self.base != '':
            self.hrdw_addr_array.append(self.hex + '+' + self.base)
            self.cnt = self.cnt + 1

        self.hex = ''
        self.base = ''
