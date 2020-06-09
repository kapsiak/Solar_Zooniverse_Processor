from solar.common import solar_event
import unittest


class TestSolarEvent(unittest.TestCase):
    def test_construction(self):
        data = [
            "SOL2007-02-16T00:52:10L153C167",
            "SOL2007-02-16T00:52:10L153C167",
            "2007-02-16T00:52:10",
            "2007-02-16T01:27:14",
            -235.928,
            -136.904,
            -1041.79,
            -932.561,
            153.831602,
            -77.4630480000001,
            "XRT",
            "NO_REQUEST",
        ]
        s = solar_event.Solar_Event(*data)
        self.assertEqual(s.event_id, data[0])
        self.assertEqual(s.sol, data[1])
        self.assertEqual(s.start_time, data[2])
        self.assertEqual(s.end_time, data[3])
        self.assertEqual(s.x_min, data[4])
        self.assertEqual(s.x_max, data[5])
        self.assertEqual(s.y_min, data[6])
        self.assertEqual(s.y_max, data[7])
        self.assertEqual(s.hgc_x, data[8])
        self.assertEqual(s.hgc_y, data[9])
        self.assertEqual(s.instrument, data[10])
        self.assertEqual(s.ssw_job_id, data[11])

    def test_size(self):
        data = [
            "SOL2007-02-16T00:52:10L153C167",
            "SOL2007-02-16T00:52:10L153C167",
            "2007-02-16T00:52:10",
            "2007-02-16T01:27:14",
            -235.928,
            -136.904,
            -1041.79,
            -932.561,
            153.831602,
            -77.4630480000001,
            "XRT",
            "NO_REQUEST",
        ]
        s = solar_event.Solar_Event(*data)
        self.assertEqual(len(s) ,12, "Incorrect Size")

        


if __name__ == '__main__':
    unittest.main()

