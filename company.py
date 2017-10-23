class Company():
    def __init__(self, name):
        self.name = name.strip()
        self.cnt = 0
        self.hex = ''
        self.base = ''
        self.hrdw_addr_array = []
        self.files = []

    def addHexMac(self, mac):
        self.hex = mac

    def addBaseMac(self, mac):
        self.base = mac
        self.trigger()

    def trigger(self):
        if self.hex != '' and self.base != '':
            self.hrdw_addr_array.append(self.hex.strip() + '+' + self.base.strip())
            self.cnt = self.cnt + 1

        self.hex = ''
        self.base = ''
