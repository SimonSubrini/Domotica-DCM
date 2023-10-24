import machine


class NRF24:
    def __init__(self, ce, spi, spi_speed=5000000, data_rate=0, channel=76, payload_size=32, address_bytes=5,
                 crc_bytes=1, pad=32, pa_level=3):
        self._ce_pin = ce
        self._spi = spi

        self.set_channel(channel)
        self.set_retransmission(1, 15)
        self.set_payload_size(payload_size)
        self.set_padding(pad)
        self.set_address_bytes(address_bytes)
        self.disable_crc()
        self.set_data_rate(data_rate)
        self.set_pa_level(pa_level)

        self._power_tx = 0
        self.power_down()
        self.flush_rx()
        self.flush_tx()
        self.power_up_rx()

    def set_channel(self, channel):
        assert 0 <= channel <= 125
        self._nrf_write_reg(0x05, channel)
        self.set_ce()

    def _nrf_write_reg(self, reg, arg):
        if type(arg) is not list:
            arg = [arg]
        self._nrf_xfer([0x20 | reg] + arg)

    def _nrf_xfer(self, data):
        data = bytes(data)  # Convertir la lista en un objeto de bytes
        response = bytearray(len(data))
        self._spi.write_readinto(data, response)
        return response

    def open_tx_pipe(self, address):
        self._nrf_xfer([0x22] + list(address))
        self._nrf_xfer(address)
        self._nrf_xfer([0x20])
        self._nrf_xfer([0x30])
        self._nrf_xfer([0x70])
        self._nrf_xfer([0x7E])

    def open_rx_pipe(self, pipe_number, address):
        assert 0 <= pipe_number < 6
        self._nrf_xfer([0x2A + pipe_number] + list(address))
        self._nrf_xfer([0x20 | (1 << pipe_number)])
        self._nrf_xfer([0x30])
        self._nrf_xfer([0x70])
        self._nrf_xfer([0x7E])
        if pipe_number == 1:
            self._nrf_xfer([0xE1])

    def start_listening(self):
        self.power_up_rx()
        self.unset_ce()
        self._nrf_xfer([0xE2])
        self.set_ce()

    def available(self):
        status = self.get_status()
        if status & 0x40:
            return True
        return False

    def read(self):
        self.unset_ce()
        payload = self._nrf_xfer(
            [0x61, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # Puedes ajustar el tamaño de lectura si tu carga útil es más grande.
        self.set_ce()
        return payload[1:]

    def set_ce(self):
        self._ce_pin.value(1)

    def unset_ce(self):
        self._ce_pin.value(0)

    def set_retransmission(self, delay, retries):
        assert 0 <= delay < 16
        assert 0 <= retries < 16

        self.unset_ce()
        self._nrf_write_reg(0x04, (delay << 4) | retries)
        self.set_ce()

    def set_payload_size(self, payload_size):
        assert -1 <= payload_size <= 32
        self._payload_size = payload_size

    def set_padding(self, pad):
        self._padding = ord(pad) if isinstance(pad, str) else pad
        assert 0 <= self._padding <= 255

    def set_address_bytes(self, address_bytes):
        assert 3 <= address_bytes <= 5
        self._address_width = address_bytes
        self.unset_ce()
        self._nrf_write_reg(0x03, self._address_width - 2)
        self.set_ce()

    def disable_crc(self):
        config = self._nrf_read_reg(0x00, 1)[0]
        mask = ~0x08 & 0xFF
        self.unset_ce()
        self._nrf_write_reg(0x00, config & mask)
        self.set_ce()

    def _nrf_read_reg(self, reg, count):
        return self._nrf_xfer([reg] + [0] * count)[1:]

    def set_crc_bytes(self, crc_bytes):
        assert 0 <= crc_bytes <= 2
        if crc_bytes == 0:
            self.disable_crc()
        else:
            config = self._nrf_read_reg(0x00, 1)[0]
            mask = 0x08 if crc_bytes == 2 else ~0x08 & 0xFF
            self.unset_ce()
            self._nrf_write_reg(0x00, config & mask)
            self.set_ce()

    def set_data_rate(self, rate):
        assert 0 <= rate <= 2
        value = self._nrf_read_reg(0x06, 1)[0] & ~0x0A & 0xFF
        if rate == 1:
            value |= 0x20
        elif rate == 2:
            value |= 0x08
        self.unset_ce()
        self._nrf_write_reg(0x06, value)
        self.set_ce()

    def set_pa_level(self, level):
        level = (level << 1) + 1
        value = self._nrf_read_reg(0x06, 1)[0] & 0xF8
        value |= level
        self.unset_ce()
        self._nrf_write_reg(0x06, value)
        self.set_ce()

    def _make_fixed_width(self, msg, width, pad):
        if isinstance(msg, str):
            msg = list(map(ord, msg))
        msg = list(msg)
        if len(msg) >= width:
            return msg[:width]
        else:
            msg.extend([pad] * (width - len(msg)))  # Aquí faltaba un paréntesis de cierre
            return msg

    def send(self, data):
        if not isinstance(data, list):
            if isinstance(data, str):
                data = list(map(ord, data))
            elif isinstance(data, int):
                data = list(data.to_bytes(-(-data.bit_length() // 8), 'little'))
            else:
                data = list(data)
        status = self.get_status()
        if status & 0x35:
            self.flush_tx()
        if self._payload_size >= -1:
            data = self._make_fixed_width(data, self._payload_size, self._padding)
        self._nrf_command([0xA0] + data)
        self.power_up_tx()

    def get_status(self):
        return self._nrf_command(0xFF)[0]

    def power_up_tx(self):
        self._power_tx = 1
        config = self._nrf_read_reg(0x00, 1)[0] & ~0x02 & 0xFF
        config |= 0x02
        self.unset_ce()
        self._nrf_write_reg(0x00, config)
        self._nrf_write_reg(0x07, 0x70)
        self.set_ce()

    def power_up_rx(self):
        self._power_tx = 0
        config = self._nrf_read_reg(0x00, 1)[0]
        self.unset_ce()
        self._nrf_write_reg(0x00, config | 0x03)
        self._nrf_write_reg(0x07, 0x70)
        self.set_ce()

    def power_down(self):
        config = self._nrf_read_reg(0x00, 1)[0]
        mask = ~0x02 & 0xFF
        self.unset_ce()
        self._nrf_write_reg(0x00, config & mask)

    def flush_rx(self):
        self._nrf_command(0xE2)

    def flush_tx(self):
        self._nrf_command(0xE1)

    def _nrf_command(self, arg):
        if type(arg) is not list:
            arg = [arg]
        return self._nrf_xfer(arg)

