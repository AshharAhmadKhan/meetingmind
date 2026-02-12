"""
MeetingMind Lambda Test Suite - Fixed version
Run: cd ~/meetingmind && python -m pytest backend/tests/ -v
"""
import json
import sys
import os
import unittest
import importlib.util
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# ── Load each Lambda as a uniquely named module ───────────────
def load_lambda(func_folder_name, module_alias):
    """Load a Lambda app.py by file path, give it a unique module name."""
    base = os.path.dirname(__file__)
    path = os.path.normpath(os.path.join(base, f'../functions/{func_folder_name}/app.py'))
    spec = importlib.util.spec_from_file_location(module_alias, path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_alias] = mod
    spec.loader.exec_module(mod)
    return mod

# ── Shared mock event builder ─────────────────────────────────
def _make_api_event(method='GET', body=None, path_params=None):
    return {
        'httpMethod': method,
        'requestContext': {
            'authorizer': {
                'claims': {'sub': 'test-user-123', 'email': 'test@example.com'}
            }
        },
        'pathParameters': path_params or {},
        'body': json.dumps(body) if body else None,
    }

# ── Shared env vars ───────────────────────────────────────────
TEST_ENV = {
    'AUDIO_BUCKET':   'test-bucket',
    'MEETINGS_TABLE': 'test-table',
    'REGION':         'ap-south-1',
    'SNS_TOPIC_ARN':  'arn:aws:sns:ap-south-1:123:test'
}


# ══════════════════════════════════════════════════════════════
# TEST: get-upload-url
# ══════════════════════════════════════════════════════════════
class TestGetUploadUrl(unittest.TestCase):

    def _load(self):
        with patch.dict(os.environ, TEST_ENV):
            with patch('boto3.client', return_value=MagicMock()), \
                 patch('boto3.resource', return_value=MagicMock()):
                return load_lambda('get-upload-url', f'upload_url_{id(self)}')

    def test_valid_upload_request(self):
        mod = self._load()

        mock_s3    = MagicMock()
        mock_table = MagicMock()
        mock_db    = MagicMock()
        mock_db.Table.return_value = mock_table
        mock_s3.generate_presigned_url.return_value = 'https://s3.presigned.url/test'
        mock_table.put_item.return_value = {}

        event = _make_api_event('POST', {
            'title': 'Weekly Standup',
            'contentType': 'audio/mpeg',
            'fileSize': 1024 * 1024
        })

        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 's3', mock_s3), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn('meetingId',  body)
        self.assertIn('uploadUrl',  body)
        self.assertIn('s3Key',      body)
        self.assertTrue(body['s3Key'].startswith('audio/'))
        print("  ✅ test_valid_upload_request PASSED")

    def test_unsupported_file_type_rejected(self):
        mod = self._load()

        event = _make_api_event('POST', {
            'title': 'Test', 'contentType': 'text/plain', 'fileSize': 100
        })

        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 's3', MagicMock()), \
             patch.object(mod, 'dynamodb', MagicMock()):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        print("  ✅ test_unsupported_file_type_rejected PASSED")

    def test_oversized_file_rejected(self):
        mod = self._load()

        event = _make_api_event('POST', {
            'title': 'Test', 'contentType': 'audio/mpeg',
            'fileSize': 600 * 1024 * 1024   # 600MB > 500MB limit
        })

        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 's3', MagicMock()), \
             patch.object(mod, 'dynamodb', MagicMock()):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        print("  ✅ test_oversized_file_rejected PASSED")


# ══════════════════════════════════════════════════════════════
# TEST: list-meetings
# ══════════════════════════════════════════════════════════════
class TestListMeetings(unittest.TestCase):

    def _load(self):
        with patch.dict(os.environ, TEST_ENV):
            with patch('boto3.client', return_value=MagicMock()), \
                 patch('boto3.resource', return_value=MagicMock()):
                return load_lambda('list-meetings', f'list_meetings_{id(self)}')

    def test_returns_meetings_for_user(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.query.return_value = {'Items': [
            {'meetingId': 'abc', 'title': 'Standup',  'status': 'DONE',
             'createdAt': '2026-02-12T10:00:00+00:00'},
            {'meetingId': 'def', 'title': 'Planning', 'status': 'DONE',
             'createdAt': '2026-02-11T10:00:00+00:00'},
        ]}
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('GET')
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertIn('meetings', body)
        self.assertEqual(len(body['meetings']), 2)
        print("  ✅ test_returns_meetings_for_user PASSED")

    def test_returns_empty_list_when_no_meetings(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.query.return_value = {'Items': []}
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('GET')
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['meetings'], [])
        print("  ✅ test_returns_empty_list_when_no_meetings PASSED")


# ══════════════════════════════════════════════════════════════
# TEST: get-meeting
# ══════════════════════════════════════════════════════════════
class TestGetMeeting(unittest.TestCase):

    def _load(self):
        with patch.dict(os.environ, TEST_ENV):
            with patch('boto3.client', return_value=MagicMock()), \
                 patch('boto3.resource', return_value=MagicMock()):
                return load_lambda('get-meeting', f'get_meeting_{id(self)}')

    def test_returns_meeting_without_transcript(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': {
            'userId':      'test-user-123',
            'meetingId':   'meeting-abc',
            'title':       'Product Review',
            'status':      'DONE',
            'transcript':  'very long raw text that should be stripped...',
            'summary':     'We discussed Q1 roadmap.',
            'decisions':   ['Ship feature X by March'],
            'actionItems': [{'id': 'action-1', 'task': 'Write spec',
                             'owner': 'Alice', 'deadline': '2026-03-01',
                             'completed': False}],
            'followUps':   ['Revisit pricing']
        }}
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('GET', path_params={'meetingId': 'meeting-abc'})
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertNotIn('transcript',  body)   # must be stripped
        self.assertIn('summary',        body)
        self.assertIn('actionItems',    body)
        self.assertEqual(len(body['actionItems']), 1)
        print("  ✅ test_returns_meeting_without_transcript PASSED")

    def test_returns_404_for_missing_meeting(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.get_item.return_value = {}   # No 'Item' key
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('GET', path_params={'meetingId': 'nonexistent'})
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 404)
        print("  ✅ test_returns_404_for_missing_meeting PASSED")


# ══════════════════════════════════════════════════════════════
# TEST: update-action
# ══════════════════════════════════════════════════════════════
class TestUpdateAction(unittest.TestCase):

    def _load(self):
        with patch.dict(os.environ, TEST_ENV):
            with patch('boto3.client', return_value=MagicMock()), \
                 patch('boto3.resource', return_value=MagicMock()):
                return load_lambda('update-action', f'update_action_{id(self)}')

    def test_mark_action_complete(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': {
            'userId':    'test-user-123',
            'meetingId': 'meeting-abc',
            'actionItems': [
                {'id': 'action-1', 'task': 'Write spec',  'completed': False},
                {'id': 'action-2', 'task': 'Review PR',   'completed': False},
            ]
        }}
        mock_table.update_item.return_value = {}
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('PUT',
            body={'completed': True},
            path_params={'meetingId': 'meeting-abc', 'actionId': 'action-1'}
        )
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertTrue(body['completed'])
        mock_table.update_item.assert_called_once()
        print("  ✅ test_mark_action_complete PASSED")

    def test_returns_404_for_unknown_action(self):
        mod = self._load()

        mock_table = MagicMock()
        mock_table.get_item.return_value = {'Item': {
            'userId':      'test-user-123',
            'meetingId':   'meeting-abc',
            'actionItems': [
                {'id': 'action-1', 'task': 'Write spec', 'completed': False},
            ]
        }}
        mock_db = MagicMock()
        mock_db.Table.return_value = mock_table

        event = _make_api_event('PUT',
            body={'completed': True},
            path_params={'meetingId': 'meeting-abc', 'actionId': 'action-NONEXISTENT'}
        )
        with patch.dict(os.environ, TEST_ENV), \
             patch.object(mod, 'dynamodb', mock_db):
            response = mod.lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 404)
        print("  ✅ test_returns_404_for_unknown_action PASSED")


# ══════════════════════════════════════════════════════════════
# TEST: process-meeting helpers
# ══════════════════════════════════════════════════════════════
class TestProcessMeetingHelpers(unittest.TestCase):

    def _load(self):
        with patch.dict(os.environ, TEST_ENV):
            with patch('boto3.client', return_value=MagicMock()), \
                 patch('boto3.resource', return_value=MagicMock()):
                return load_lambda('process-meeting', f'process_meeting_{id(self)}')

    def test_get_format_detection(self):
        mod = self._load()
        self.assertEqual(mod._get_format('audio/file.mp3'),     'mp3')
        self.assertEqual(mod._get_format('audio/file.wav'),     'wav')
        self.assertEqual(mod._get_format('audio/file.m4a'),     'mp4')
        self.assertEqual(mod._get_format('audio/file.webm'),    'webm')
        self.assertEqual(mod._get_format('audio/file.unknown'), 'mp3')
        print("  ✅ test_get_format_detection PASSED")

    def test_key_parsing(self):
        key      = "audio/user123__meeting456__Weekly-Standup.mp3"
        filename = key.split('/')[-1]
        parts    = filename.rsplit('.', 1)[0].split('__')
        self.assertEqual(parts[0], 'user123')
        self.assertEqual(parts[1], 'meeting456')
        self.assertEqual(parts[2], 'Weekly-Standup')
        print("  ✅ test_key_parsing PASSED")

    def test_s3_key_format_built_correctly(self):
        """Verify the key format process-meeting will receive from get-upload-url."""
        user_id    = 'usr-abc'
        meeting_id = 'mtg-123'
        title      = 'Q1 Planning'
        safe_title = title.replace(' ', '-').replace('/', '-')
        ext        = 'mp3'
        key        = f"audio/{user_id}__{meeting_id}__{safe_title}.{ext}"

        # Now parse it back (same logic as process-meeting)
        filename = key.split('/')[-1]
        parts    = filename.rsplit('.', 1)[0].split('__')
        self.assertEqual(parts[0], user_id)
        self.assertEqual(parts[1], meeting_id)
        self.assertEqual(parts[2], 'Q1-Planning')
        print("  ✅ test_s3_key_format_built_correctly PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
