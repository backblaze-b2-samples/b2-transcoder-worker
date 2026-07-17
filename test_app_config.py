import importlib
import os
import sys
import unittest
from unittest.mock import patch


BASE_ENV = {
    'B2_APPLICATION_KEY_ID': 'dummy-key-id',
    'B2_APPLICATION_KEY': 'dummy-key',
    'B2_BUCKET_NAME': 'dummy-bucket',
    'B2_REGION': 'us-west-001',
}


def import_app_with_env(env):
    sys.modules.pop('app', None)
    with patch.dict(os.environ, env, clear=True):
        return importlib.import_module('app')


class AppConfigTest(unittest.TestCase):
    def tearDown(self):
        sys.modules.pop('app', None)

    def test_new_env_configures_b2_s3_client(self):
        app = import_app_with_env(BASE_ENV)

        self.assertEqual(app.bucket_name, 'dummy-bucket')
        self.assertEqual(
            app.s3.meta.endpoint_url,
            'https://s3.us-west-001.backblazeb2.com',
        )
        self.assertEqual(app.s3.meta.region_name, 'us-west-001')
        self.assertIn(
            'b2-transcoder-worker (backblaze-b2-samples)',
            app.s3._client_config.user_agent,
        )

    def test_missing_region_has_clear_error(self):
        env = dict(BASE_ENV)
        env.pop('B2_REGION')

        with self.assertRaises(SystemExit) as exc:
            import_app_with_env(env)

        self.assertIn('B2_REGION is required', str(exc.exception))

    def test_missing_bucket_has_clear_error(self):
        env = dict(BASE_ENV)
        env.pop('B2_BUCKET_NAME')

        with self.assertRaises(SystemExit) as exc:
            import_app_with_env(env)

        self.assertIn('B2_BUCKET_NAME is required', str(exc.exception))

    def test_rejects_region_with_slash(self):
        env = dict(BASE_ENV, B2_REGION='attacker.example/x')

        with self.assertRaises(SystemExit) as exc:
            import_app_with_env(env)

        self.assertIn('B2_REGION must be a Backblaze region token', str(exc.exception))

    def test_rejects_region_with_at_sign(self):
        env = dict(BASE_ENV, B2_REGION='us-west-001@attacker.example/x')

        with self.assertRaises(SystemExit) as exc:
            import_app_with_env(env)

        self.assertIn('B2_REGION must be a Backblaze region token', str(exc.exception))


if __name__ == '__main__':
    unittest.main()
