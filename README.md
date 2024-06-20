# CryptoChallenges Assignment README

## Project Overview

I wrote a code to solve the hash and decrypt challenges set by the CryptoChallenges API. This code creates the challenges by sending a POST request (no body needed) to, respectively, the `/hash` and `/decrypt` paths (collections). A challenge is deleted automatically by the server after remaining unsolved for 1 hour or 3 unsuccessful attempts. The objective of my code is to delete the challenge beforehand by providing a solution.

## API Details

### Challenge Creation

A challenge resource is created and returned in response to a POST request. GET and DELETE methods can be used on the created resource - the resource's path is the name of the collection followed by the `challengeId` returned in the create request, e.g., `/decrypt/1683322654`.

- **GET Request**: Returns the public information about the challenge.
- **DELETE Request**: Expected to carry a payload that solves the challenge. If the solution is correct, the challenge is deleted. If it is not, deletion fails.

### Decrypt Challenge

I wrote code that handles the decrypt challenges. The POST and GET requests on a decrypt resource return a JSON document such as this one:

```json
{
    "challengeId": "3386580009",
    "ciphertext": "lrbzHhWckb2dd01IX6SmbPuasEALboIpRvbFvJU1ukBt//rd9gk/OEfYJhcJzNgrBV5EvYPm1xmNZSykdiilHI6KD3tpZ1by4A8Ju232raAh+/l/jpViGPVAMgPjnCkSOnMl3gIBHIHh7AU4SkXmEW4hIy8lIm0/VKZsdsfzfCE28dzRX70zBozX7JxQzTfA",
    "key": "fKyVwkSOnL95K1u8WATH6FE+V9EH2tROoQayhh2jMz0=",
    "nonce": "IRjPa3Q+NP8osVCZpGl+aQuilVznnrS+"
}
```

The `challengeId` identifies the resource. The `ciphertext` is a randomly generated message, encrypted with XSalsa20 and using a Poly1305 MAC for authentication with the `key` and `nonce` properties. Ciphertext, key, and nonce are all base64 encoded binary data. The payload of the DELETE request for the decrypt challenge is a JSON document with a `plaintext` property such that:

```
Ekey(nonce, plaintext) = ciphertext
```

where `key`, `nonce`, and `ciphertext` are all decryption challenge properties and `E` is the authenticated encryption algorithm.

### Hash Challenge

I also wrote code to handle the hash challenges. The POST and GET requests on a hash resource return a JSON document such as this one:

```json
{
    "attemptsRemaining": "3",
    "challengeId": "4249615771",
    "message": "J9Hy3KPTWXz1QkDFUIn1m0tqV2BUC7CG0m2ohQ5ksfokmhgISCKYMSE+9oXSsFWc+b5Mib6zEN8fDPXJNGWopg=="
}
```

The `challengeId` identifies the resource. The `message` is a randomly generated message. `attemptsRemaining` tells how many times you can submit a candidate solution before the challenge is automatically deleted. The payload of the DELETE request for the hash challenge is a JSON document with a `prefix` property such that prepending it to the challenge's message results in a Blake2 hash with the 2 leading bytes equal to 0.

Like the `/decrypt` endpoint, `/hash` base64 encodes binary data it sends and expects binary data it receives to be base64 encoded.
