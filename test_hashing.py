import unittest
from unittest.mock import patch, MagicMock
import base64
import threading
import hashlib
from nacl.utils import random
import hashing

class TestHashingChallenge(unittest.TestCase):

    @patch('hashing.requests.post')
    def test_create_challenge(self, mock_post):
        mock_post.return_value.json.return_value = {'challengeId': '12345'}
        challenge = hashing.create_challenge('hash')
        self.assertEqual(challenge['challengeId'], '12345')

    @patch('hashing.requests.delete')
    def test_delete_challenge(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        response = hashing.delete_challenge('hash', '12345', {'prefix': 'testprefix'})
        self.assertEqual(response.status_code, 200)

    @patch('hashing.requests.get')
    def test_solve_hash_challenge(self, mock_get):
        # Mock the get response to return a specific message
        message = b'testmessage'
        mock_get.return_value.json.return_value = {'message': base64.b64encode(message).decode('utf-8')}
        
        # Use a fixed prefix to ensure consistency
        fixed_prefix = b'fixedprefix'
        candidate = fixed_prefix + message
        hash_result = hashlib.blake2b(candidate, digest_size=32).digest()
        
        while hash_result[:2] != b'\x00\x00':
            fixed_prefix = random(16)
            candidate = fixed_prefix + message
            hash_result = hashlib.blake2b(candidate, digest_size=32).digest()
        
        expected_prefix = base64.b64encode(fixed_prefix).decode('utf-8')
        
        with patch('hashing.random', return_value=fixed_prefix):
            hashing.verbose = False  # Disable printing for unit tests
            solution = hashing.solve_hash_challenge('12345', threading.Event())
            self.assertEqual(solution['prefix'], expected_prefix)

if __name__ == '__main__':
    unittest.main()
