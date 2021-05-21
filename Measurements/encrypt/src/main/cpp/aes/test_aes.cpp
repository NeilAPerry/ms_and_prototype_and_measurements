//
// Created by gj on 8/26/2020.
//
#include "test_aes.h"
#include "aes_wrapper.h"
#include "base64.h"
#include "../common.h"
#include <iostream>

#include <random>
#include <string>

using namespace std;

int test_aes() {
    unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1] = "0123456789ABCDEF";
    unsigned char IV_HTTP[AES_BLOCK_SIZE] = {
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0
    };

    auto *aes = new CbdAes();
    aes->setAesKey(KEY_HTTP, 16);
    aes->setAesIv(IV_HTTP, 16);

    // encrypt aes
    string msg = string("hello,world!2. 点击切换tab的展示的主页面不展示返回icon；当进入下一级页面的时候，在页面的右下位置增加一个返回icon；");
    const auto *in = reinterpret_cast<const unsigned char *>(msg.c_str());
    size_t in_len = msg.size() + 1;
    unsigned char *encrypted = nullptr;
    int encrypted_len = aes->aesEncrypt(in, in_len, &encrypted);
    if (encrypted_len == FAILURE) {
        LOGW("Encryption failed\n");
        return FAILURE;
    }

//    // decrypt aes
//    unsigned char *decrypted = nullptr;
//    int decrypted_len = aes->aesDecrypt(encrypted, encrypted_len, (unsigned char **) &decrypted);
//    if (decrypted_len == FAILURE) {
//        LOGW("Decryption failed\n");
//        return FAILURE;
//    }

    // encode base64
    char *b64_encoded = base64Encode(encrypted, encrypted_len);
    LOGW("Encrypted message: %s\n", b64_encoded);

    // decode base64
    unsigned char *b64_decoded = nullptr;
    int b64_decode_len = base64Decode(b64_encoded, strlen(b64_encoded), &b64_decoded);

    // decrypt aes
    unsigned char *decrypted = nullptr;
    int decrypted_len = aes->aesDecrypt(b64_decoded, b64_decode_len, (unsigned char **) &decrypted);
    if (decrypted_len == FAILURE) {
        LOGW("Decryption failed\n");
        return FAILURE;
    }

    LOGW("Decrypted message: %s\n", decrypted);

    free(b64_encoded);
    free(b64_decoded);
    free(encrypted);
    free(decrypted);

    return SUCCESS;
}

std::string random_string(int l)
{
    mt19937 generator{random_device{}()};

    //modify range according to your need "A-Z","a-z" or "0-9" or whatever you need.
    uniform_int_distribution<int> distribution{'a', 'z'};

    auto generate_len = l; //modify length according to your need
    string rand_str(generate_len, '\0');
    for(auto& dis: rand_str)
        dis = distribution(generator);
    return rand_str;
}

void measure_aes() {
    std::string temp = random_string(16);

    unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1]; // = tempChars; //"0123456789ABCDEF";
    strcpy(reinterpret_cast<char *const>(KEY_HTTP), temp.c_str());

    unsigned char IV_HTTP[AES_BLOCK_SIZE] = {
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0
    };

    auto *aes = new CbdAes();
    aes->setAesKey(KEY_HTTP, 16);
    aes->setAesIv(IV_HTTP, 16);

    // encrypt aes
    string msg = random_string(288);
//    LOGW("Original message: %s\n", msg.c_str());
    const auto *in = reinterpret_cast<const unsigned char *>(msg.c_str());
    size_t in_len = msg.size() + 1;
    unsigned char *encrypted = nullptr;

    std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
    int encrypted_len = aes->aesEncrypt(in, in_len, &encrypted);
    std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
    auto enc_time = std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count();

    if (encrypted_len == FAILURE) {
        LOGW("Encryption failed\n");
    }

    // encode base64
    char *b64_encoded = base64Encode(encrypted, encrypted_len);
//    LOGW("Encrypted message: %s\n", b64_encoded);

    // decode base64
    unsigned char *b64_decoded = nullptr;
    int b64_decode_len = base64Decode(b64_encoded, strlen(b64_encoded), &b64_decoded);

    // decrypt aes
    unsigned char *decrypted = nullptr;

    t1 = std::chrono::high_resolution_clock::now();
    int decrypted_len = aes->aesDecrypt(b64_decoded, b64_decode_len, (unsigned char **) &decrypted);
    t2 = std::chrono::high_resolution_clock::now();
    auto dec_time = std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count();

    if (decrypted_len == FAILURE) {
        LOGW("Decryption failed\n");
    }

//    LOGW("Decrypted message: %s\n", decrypted);

    free(b64_encoded);
    free(b64_decoded);
    free(encrypted);
    free(decrypted);

    LOGW("aes enc time: %lld", enc_time);
    LOGW("aes dec time: %lld", dec_time);
}

char* do_aes_encrypt(unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1], string msg) {

    unsigned char IV_HTTP[AES_BLOCK_SIZE] = {
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0
    };

    auto *aes = new CbdAes();
    aes->setAesKey(KEY_HTTP, 16);
    aes->setAesIv(IV_HTTP, 16);

    // encrypt aes
    const auto *in = reinterpret_cast<const unsigned char *>(msg.c_str());
    size_t in_len = msg.size() + 1;
    unsigned char *encrypted = nullptr;

    int encrypted_len = aes->aesEncrypt(in, in_len, &encrypted);

    if (encrypted_len == FAILURE) {
        LOGW("Encryption failed\n");
    }

    // encode base64
    char *b64_encoded = base64Encode(encrypted, encrypted_len);



    free(encrypted);

    return b64_encoded;
}

std::string do_aes_decrypt(unsigned char KEY_HTTP[AES_BLOCK_SIZE + 1], char *b64_encoded) {
    unsigned char IV_HTTP[AES_BLOCK_SIZE] = {
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
            0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0
    };

    auto *aes = new CbdAes();
    aes->setAesKey(KEY_HTTP, 16);
    aes->setAesIv(IV_HTTP, 16);

    // decode base64
    unsigned char *b64_decoded = nullptr;
    int b64_decode_len = base64Decode(b64_encoded, strlen(b64_encoded), &b64_decoded);

    // decrypt aes
    unsigned char *decrypted = nullptr;

    int decrypted_len = aes->aesDecrypt(b64_decoded, b64_decode_len, (unsigned char **) &decrypted);

    if (decrypted_len == FAILURE) {
        LOGW("Decryption failed\n");
    }

    free(decrypted);

    std::string pt(reinterpret_cast<char*>(decrypted));

    return pt;
}