"""Data buffer regression tests using captured RC-102 records."""

import datetime
import unittest

from radiacode import DoseCounter, RareData, RawData, RealTimeData
from radiacode.bytes_buffer import BytesBuffer
from radiacode.decoders.databuf import decode_VS_DATA_BUF


class DataBufTests(unittest.TestCase):
    base_time = datetime.datetime(2026, 1, 1)

    def test_realtime_alignment(self):
        # Consecutive captured records (sequence 110 and 111).
        br = BytesBuffer(
            bytes.fromhex(
                '6e0000bbceffff0000ab40f706eb363500b20040200000'
                '6f0001a20000000000c0406c09f935'
            )
        )
        records = decode_VS_DATA_BUF(br, self.base_time, ignore_errors=False)
        self.assertEqual(len(records), 2)
        realtime, raw = records
        self.assertIsInstance(realtime, RealTimeData)
        assert isinstance(realtime, RealTimeData)
        self.assertEqual(realtime.count_rate, 5.34375)
        self.assertAlmostEqual(realtime.dose_rate, 7.004356575635029e-06, places=14)
        self.assertEqual(realtime.count_rate_err, 5.3)
        self.assertEqual(realtime.dose_rate_err, 17.8)
        self.assertEqual(realtime.flags, 0x2040)
        self.assertEqual(realtime.real_time_flags, 0)
        self.assertEqual(realtime.dt, self.base_time - datetime.timedelta(seconds=126.13))
        self.assertIsInstance(raw, RawData)
        assert isinstance(raw, RawData)
        self.assertEqual(raw.count_rate, 6.0)
        self.assertEqual(br.size(), 0)

    def test_realtime_flags_high_byte(self):
        # Synthetic variant of the captured record with a nonzero high byte.
        br = BytesBuffer(bytes.fromhex('6e0000bbceffff0000ab40f706eb363500b20040203412'))
        (record,) = decode_VS_DATA_BUF(br, self.base_time, ignore_errors=False)
        assert isinstance(record, RealTimeData)
        self.assertEqual(record.real_time_flags, 0x1234)
        self.assertEqual(br.size(), 0)

    def test_dose_counter_alignment(self):
        # Consecutive captured records: counter, historical batch, status.
        br = BytesBuffer(
            bytes.fromhex(
                '720004ce7074ff3707000000b0'
                '730102445574ff030080250000'
                'ac010000abaa8e400784e3362f0100b0'
                'b101000055559040fb81d8365a0100b0'
                'c6010000555597403ab70637270100b0'
                '7400036adc74ffce0e14007b4f653bd612102740b0'
            )
        )
        # Historical batches are still skipped by the current decoder.
        records = decode_VS_DATA_BUF(br, self.base_time, ignore_errors=False)
        self.assertEqual(len(records), 2)
        counter, status = records
        self.assertIsInstance(counter, DoseCounter)
        assert isinstance(counter, DoseCounter)
        self.assertEqual(counter.dose_counter, 1847)
        self.assertEqual(counter.flags, 0xB000)
        self.assertEqual(counter.dt, self.base_time - datetime.timedelta(seconds=91461.62))
        self.assertIsInstance(status, RareData)
        assert isinstance(status, RareData)
        self.assertEqual(status.duration, 1314510)
        self.assertEqual(br.size(), 0)


if __name__ == '__main__':
    unittest.main()
