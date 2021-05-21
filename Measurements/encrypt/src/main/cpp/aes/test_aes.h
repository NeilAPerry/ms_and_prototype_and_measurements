//
// Created by areful on 2020/8/27.
//

#ifndef NDKUSEOPENSSL_TEST_AES_H
#define NDKUSEOPENSSL_TEST_AES_H

#include <string>
#include <openssl/aes.h>

int test_aes();
void measure_aes();
std::string random_string(int l);
char* do_aes_encrypt(unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1], std::string msg);
std::string do_aes_decrypt(unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1], char *b64_encoded);

#endif //NDKUSEOPENSSL_TEST_AES_H
