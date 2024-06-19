import unittest
from unittest.mock import patch
import base64
from decrypting import fetch_decrypt_challenge, decode_base64, decrypt_data, submit_decrypt_solution

class TestDecryptingChallenge(unittest.TestCase):

    @patch('decrypting.requests.post')
    def test_fetch_decrypt_challenge(self, mock_post):
        mock_post.return_value.json.return_value = {
            "challengeId": "12345",
            "key": "somekey",
            "ciphertext": "someciphertext",
            "nonce": "somenonce"
        }
        challenge_id, key, ciphertext, nonce = fetch_decrypt_challenge()
        self.assertEqual(challenge_id, "12345")
        self.assertEqual(key, "somekey")
        self.assertEqual(ciphertext, "someciphertext")
        self.assertEqual(nonce, "somenonce")

    def test_decode_base64(self):
        encoded_data = base64.b64encode(b"testdata").decode('utf-8')
        decoded_data = decode_base64(encoded_data)
        self.assertEqual(decoded_data, b"testdata")

    @patch('decrypting.SecretBox')
    def test_decrypt_data(self, mock_secret_box):
        mock_secret_box.return_value.decrypt.return_value = b"decrypteddata"
        decrypted_data = decrypt_data(b"ciphertext", b"key", b"nonce")
        self.assertEqual(decrypted_data, base64.b64encode(b"decrypteddata").decode('utf-8'))

    @patch('decrypting.requests.delete')
    def test_submit_decrypt_solution(self, mock_delete):
        mock_delete.return_value.status_code = 204
        status_code = submit_decrypt_solution("12345", "plaintext")
        self.assertEqual(status_code, 204)

if __name__ == '__main__':
    unittest.main()
