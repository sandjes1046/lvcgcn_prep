import unittest
from unittest import mock
import loguru
loguru.logger = mock.Mock()
import tempfile
import torosgcn
import smtplib
smtplib.SMTP = mock.Mock()


class TestConfig(unittest.TestCase):
    @mock.patch('torosgcn.config._yaml')
    def test_load_config(self, mock_yaml):
        torosgcn.config._CONFIG_IS_LOADED = False
        fp = tempfile.NamedTemporaryFile("w+")
        torosgcn.config.CONFIG_PATH = fp.name
        fp.write('Test')
        fp.seek(0)
        torosgcn.config.load_config()
        self.assertTrue(mock_yaml.full_load.called)
        fp.close()

    def test_get_config(self):
        torosgcn.config._CONFIG_IS_LOADED = False
        fp = tempfile.NamedTemporaryFile("w+")
        torosgcn.config.CONFIG_PATH = fp.name
        fp.write('Test: Param01')
        fp.seek(0)
        config_dict = torosgcn.config.get_config()
        self.assertEqual({'Test': 'Param01'}, config_dict)
        fp.close()

    def test_get_config_for_key(self):
        torosgcn.config._CONFIG_IS_LOADED = False
        fp = tempfile.NamedTemporaryFile("w+")
        torosgcn.config.CONFIG_PATH = fp.name
        fp.write("One: Param01\nTwo: Param02")
        fp.seek(0)
        first_val = torosgcn.config.get_config_for_key('One')
        second_val = torosgcn.config.get_config_for_key('Two')
        self.assertEqual(first_val, 'Param01')
        self.assertEqual(second_val, 'Param02')
        fp.close()

    def test_init_logger(self):
        torosgcn.config._CONFIG_IS_LOADED = False
        fp = tempfile.NamedTemporaryFile("w+")
        torosgcn.config.CONFIG_PATH = fp.name
        fp.write("Logging: {"
                 "  File: logfilename,"
                 "  Log Level: INFO"
                 "}")
        fp.seek(0) 
        torosgcn.config.init_logger()
        self.assertTrue(loguru.logger.add.called)


class TestListen(unittest.TestCase):
    def setUp(self):
        self.info = {'role': 'drill',
                     'graceid': 'D190422ab',
                     'alert_type': 'Initial',
                     'eventpage': 'http://someurl.com/view',
                     'skymap_url': 'http://download/skymap',
                     'bnsprob': 0.7,
                     'nsbhprob': 0.1,
                     'bbhprob': 0.0,
                     'nsprob': 0.5,
                     'remnprob': 0.99,
                     'gcndatetime': '2019-04-22T00:00:00',
                     'datetime': '2019-04-22T03:12:23',
                    }
        from astropy.coordinates import EarthLocation
        self.obs = [
            {
             'name': 'EABA',
             'location': EarthLocation.from_geodetic(-64.5467, -31.5983, 1350),
            },
            {
             'name': 'CTMO',
             'location': EarthLocation.from_geodetic(-97.568956, 25.995789, 12),
            },
            ]
        from astropy.io import ascii
        import numpy as np
        from . import sample_data
        self.ntarg = 10
        t_targets = ascii.read(sample_data.minicat)[:2 * self.ntarg]
        t_targets['Likelihood'] = np.random.random(2 * self.ntarg)
        self.obs_trg = self.obs.copy()
        self.obs_trg[0]['targets'] = t_targets[:self.ntarg]
        self.obs_trg[1]['targets'] = t_targets[self.ntarg:]

    def test_sendemail(self):
        test_config = ("Email Configuration: {\n"
                       "  SMTP Domain: mta.ad.utrgv.edu:25,\n"
                       "  Sender Address: torosligoalerts@mta.ad.utrgv.edu,\n"
                       "  Login Required: false,\n"
                       "  Username: null,  # null if not needed\n"
                       "  Password: null,  # null if not needed\n"
                       "  Recipients File: recipients.txt\n"
                       "}")
        torosgcn.config._CONFIG_IS_LOADED = False
        fp = tempfile.NamedTemporaryFile("w+")
        torosgcn.config.CONFIG_PATH = fp.name
        fp.write(test_config)
        fp.seek(0)

        msg_text = "If you received this email, the test passed OK.\n"
        subject = "Test case: test_sendemail_one_recip"
        recipient = ['user@example.com', ]
        torosgcn.listen.sendemail(msg_text, subject, recipients=recipient)
        self.assertTrue(smtplib.SMTP.called)

    @mock.patch('torosgcn.listen.config')
    @mock.patch('torosgcn.listen.sendemail')
    def test_sendalertemail(self, mock_sendemail, mock_config):
        mock_config.get_config_for_key.return_value(['admin@example.com'])
        torosgcn.listen.sendalertemail("some path", self.info)
        self.assertTrue(mock_sendemail.called)
        self.assertTrue(mock_config.get_config_for_key.called)
        (msg_text, subject), kwargs = mock_sendemail.call_args
        self.assertTrue('DRILL' in subject)
        self.assertTrue('Initial' in subject)
        self.assertTrue('D190422ab' in subject)
        self.assertTrue('D190422ab' in msg_text)
        self.assertTrue('http://someurl.com/view' in msg_text)
        self.assertTrue('http://download/skymap' in msg_text)
        self.assertTrue('0.7' in msg_text)
        self.assertTrue('0.1' in msg_text)
        self.assertTrue('0.0' in msg_text)
        self.assertTrue('0.5' in msg_text)
        self.assertTrue('0.99' in msg_text)
        self.assertTrue(kwargs.get('recipients') is None)
        self.assertEqual(kwargs.get('attachments'),  ["some path"])

    def test_getinfo(self):
        from . import sample_data
        from lxml.etree import fromstring
        for voe, at_string in zip(
                       (sample_data.preliminary_voe,
                        sample_data.initial_voe,
                        sample_data.update_voe),
                       ('Preliminary', 'Initial', 'Update')):
            root = fromstring(voe)
            info_ret = torosgcn.listen.getinfo(root)
            self.assertTrue(isinstance(info_ret, dict))
            self.assertEqual(info_ret.get('role'), 'test')
            self.assertTrue('graceid' in info_ret)
            self.assertEqual(info_ret.get('alert_type'), at_string)
            self.assertTrue('eventpage' in info_ret)
            self.assertTrue('skymap_url' in info_ret)
            self.assertTrue('bnsprob' in info_ret)
            self.assertTrue('nsbhprob' in info_ret)
            self.assertTrue('bbhprob' in info_ret)
            self.assertTrue('nsprob' in info_ret)
            self.assertTrue('remnprob' in info_ret)
            self.assertTrue('gcndatetime' in info_ret)
            self.assertTrue('datetime' in info_ret)

        # Retractions are special
        root = fromstring(sample_data.retraction_voe)
        info_ret = torosgcn.listen.getinfo(root)
        self.assertTrue(isinstance(info_ret, dict))
        self.assertEqual(info_ret.get('role'), 'test')
        self.assertTrue('graceid' in info_ret)
        self.assertEqual(info_ret.get('alert_type'), 'Retraction')
        self.assertTrue('eventpage' in info_ret)
        self.assertTrue(info_ret.get('skymap_url') is None)
        self.assertTrue(info_ret.get('bnsprob') is None)
        self.assertTrue(info_ret.get('nsbhprob') is None)
        self.assertTrue(info_ret.get('bbhprob') is None)
        self.assertTrue(info_ret.get('nsprob') is None)
        self.assertTrue(info_ret.get('remnprob') is None)
        self.assertTrue('gcndatetime' in info_ret)
        self.assertTrue('datetime' in info_ret)

    @mock.patch('requests.session')
    @mock.patch('torosgcn.listen.sendemail')
    @mock.patch('torosgcn.listen.config.get_config_for_key')
    @mock.patch('torosgcn.listen.scheduler.generate_targets')
    def test_upload_gcnnotice(self,
            mock_gen_targets, mock_get_conf, mock_sendemail, mock_session):
        mock_gen_targets.return_value = self.obs_trg
        def get_conf(arg):
            if arg == 'Broker Upload':
                return {'site url': 'https://toros.utrgv.edu/',
                        'login url': 'https://toros.utrgv.edu/account/login/',
                        'uploadjson url': 'https://toros.utrgv.edu/broker/uploadjson/',
                        'logout url': 'https://toros.utrgv.edu/account/logout/',
                        'username': 'admin',
                        'password': 'yourpassword'}
            elif arg == 'Admin Emails':
                return ["admin@example.com"]
            else:
                return None
        mock_get_conf.side_effect = get_conf
        torosgcn.listen.upload_gcnnotice(self.info)
        self.assertTrue(mock_sendemail.called)
        self.assertTrue(mock_session.called)


class TestScheduler(unittest.TestCase):
    def setUp(self):
        from astropy.coordinates import EarthLocation
        self.obs = [
            {
             'name': 'EABA',
             'location': EarthLocation.from_geodetic(-64.5467, -31.5983, 1350),
            },
            {
             'name': 'CTMO',
             'location': EarthLocation.from_geodetic(-97.568956, 25.995789, 12),
            },
            ]

        from astropy.io import ascii
        import numpy as np
        from . import sample_data
        self.ntarg = 10
        t_targets = ascii.read(sample_data.minicat)[:2 * self.ntarg]
        t_targets['Likelihood'] = np.random.random(2 * self.ntarg)
        self.obs_trg = self.obs.copy()
        self.obs_trg[0]['targets'] = t_targets[:self.ntarg]
        self.obs_trg[1]['targets'] = t_targets[self.ntarg:]

    def test_alpha_cuts(self):
        from astropy.time import Time
        observation_time = Time("2019-04-22T00:00:00")
        lo_alpha, hi_alpha = torosgcn.scheduler.alpha_cuts(observation_time)
        self.assertNotEqual(lo_alpha, hi_alpha)
        self.assertFalse(lo_alpha is None)
        self.assertFalse(hi_alpha is None)

    def test_broker_uploadstring(self):
        ret_string = torosgcn.scheduler.broker_uploadstring(self.obs)
        self.assertTrue(isinstance(ret_string, str))
        self.assertTrue('EABA' in ret_string)
        self.assertTrue('CTMO' in ret_string)
        self.assertTrue(len(ret_string.split(';')), 2)
        eaba, ctmo = ret_string.split(';')
        eaba_name, eaba_targets = eaba.split(":")
        ctmo_name, ctmo_targets = ctmo.split(":")
        self.assertEqual(eaba_name.strip(), "EABA")
        self.assertEqual(len(eaba_targets.split(',')), self.ntarg)
        self.assertEqual(ctmo_name.strip(), "CTMO")
        self.assertEqual(len(ctmo_targets.split(',')), self.ntarg)

    @mock.patch('torosgcn.scheduler.config')
    def test_broker_json(self, mock_config):
        import json
        # Patching for get_config_for_key("LIGO Run")
        mock_config.get_config_for_key.return_value = 'O3'
        info = {'role': 'S',
                'graceid': 'S190422ab',
                'datetime': '2019-04-22T03:23:12',
                'alert_type': 'Preliminary',
                'gcndatetime': '2019-04-22T00:00:00',
               }
        json_str = torosgcn.scheduler.broker_json(self.obs_trg, info)
        self.assertFalse(json_str is None)
        self.assertTrue(isinstance(json.loads(json_str), dict))
        self.assertTrue('S190422ab' in json_str)
        self.assertTrue('2019-04-22T03:23:12' in json_str)
        self.assertTrue('Preliminary' in json_str)
        self.assertTrue('O3' in json_str)

    @mock.patch('torosgcn.scheduler.config')
    def test_generate_targets(self, mock_config):
        cat_filters = {'NUM_TARGETS': 30,
                       'MAX_DIST': 120,
                       'MAX_APP_MAG': 19.0,
                       'MAX_ABS_MAG': -17.5,
                       }
        mock_config.get_config_for_key.side_effect = [
            self.obs, "./torosgcn/aux_files/GWGCCatalog.txt", cat_filters]
        skymap_path = "./tests/test_bayestar.fits.gz"
        obs_ret = torosgcn.scheduler.generate_targets(skymap_path)
        self.assertEqual(len(obs_ret), 2)
        eaba = obs_ret[0]
        ctmo = obs_ret[1]
        self.assertTrue('name' in eaba)
        self.assertEqual('EABA', eaba.get('name'))
        self.assertTrue('name' in ctmo)
        self.assertEqual('CTMO', ctmo.get('name'))
        self.assertTrue('targets' in eaba)
        for targets in [eaba.get('targets'), ctmo.get('targets')]:
            self.assertTrue('Name' in targets.colnames)
            self.assertTrue('RA' in targets.colnames)
            self.assertTrue('Dec' in targets.colnames)
            self.assertTrue('Likelihood' in targets.colnames)
            self.assertEqual(len(targets), 30)

if __name__ == '__main__':
    unittest.main()
