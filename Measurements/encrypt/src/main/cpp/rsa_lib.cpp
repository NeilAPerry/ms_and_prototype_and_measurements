//
// Created by areful on 2020/9/2.
//

#include "rsa_lib.h"
#include "rsa/rsa.h"
#include "b64/b64.h"
#include "utils.h"
#include<string>
#include "../common.h"

#include "aes/test_aes.h"

#include <openssl/sha.h>
#include <openssl/ec.h>
#include <openssl/aes.h>
#include <cstdint>
#include <array>
#include <inttypes.h>

#include <chrono>
#include <random>

extern "C" {
    #include "ecelgamal.h"
    #include "crtecelgamal.h"
}

using namespace std;

dig_t rand_uint64(void) {
    dig_t r = 0;
    for (int i=0; i<64; i += 15 /*30*/) {
        r = r*((uint64_t)RAND_MAX + 1) + rand();
    }
    return r;
}

dig_t rand_uint32(void) {
    dig_t r = 0;
    for (int i=0; i<32; i += 15 /*30*/) {
        r = r*((uint32_t)RAND_MAX + 1) + rand();
    }
    return r;
}

dig_t large_rand() {
    const uint64_t min = 0;
    const uint64_t max = 36435345; // 4294967295;
    std::default_random_engine generator;
    std::uniform_int_distribution<uint64_t> distribution(min,max);
    uint64_t random_int = distribution(generator);
    return (dig_t) random_int;
}

int elgamal() {
    LOGW("in elgamal\n");

    crtgamal_params_t params;
    crtgamal_key_t key, key_decoded;
    crtgamal_ciphertext_t cipher, cipher_after;
    bsgs_table_t table;
    dig_t plain = rand_uint64(), res, res2;
    unsigned char *buff;
    size_t size, size_ciphertext;

    crtgamal_init(CURVE_256_SEC); // try CURVE_256_SEC instead
    crt_params_create_default(params, DEFAULT_32_INTEGER_PARAMS);

    crtgamal_generate_keys(key, params);

    std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
    crtgamal_encrypt(cipher, key, plain);
    std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
    auto enc_time = std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count();

    size_ciphertext = crt_get_encoded_ciphertext_size(cipher);
    buff = (unsigned char *) malloc(size_ciphertext);
    crt_encode_ciphertext(buff, (int) size_ciphertext, cipher);
    crt_decode_ciphertext(cipher_after, buff, (int) size_ciphertext);
    free(buff);

    //size = get_encoded_key_size(key);
    //buff = (unsigned char *) malloc(size);
    //encode_key(buff, size, key);
    //decode_key(key_decoded, buff, size);


    gamal_init_bsgs_table(table, 1L << 8);

    t1 = std::chrono::high_resolution_clock::now();
    crtgamal_decrypt(&res, key, cipher_after, table);
    t2 = std::chrono::high_resolution_clock::now();
    auto dec_time = std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count();

    gamal_free_bsgs_table(table);
    crt_params_free(params);
    crtgamal_ciphertext_free(cipher);
    crtgamal_ciphertext_free(cipher_after);
    gamal_deinit();

//    std::string enc = "enc_time: ";
//    std::string dec = "dec_time: ";
//    enc += std::to_string(enc_time / 1000000.0);
//    dec += std::to_string(dec_time / 1000000.0);

    LOGW("enc time: %lld", enc_time);
    LOGW("dec time: %lld", dec_time);


    return 0;
}

bool simpleSHA256(void* input, unsigned long length, unsigned char* md)
{
    SHA256_CTX context;
    if(!SHA256_Init(&context))
        return false;

    if(!SHA256_Update(&context, (unsigned char*)input, length))
        return false;

    if(!SHA256_Final(md, &context))
        return false;

    return true;
}

std::array<std::uint8_t, 8> to_bytes(std::uint64_t x) {
    std::array<std::uint8_t, 8> b;
    b[0] = x >> 8*0;
    b[1] = x >> 8*1;
    b[2] = x >> 8*2;
    b[3] = x >> 8*3;
    b[4] = x >> 8*4;
    b[5] = x >> 8*5;
    b[6] = x >> 8*6;
    b[7] = x >> 8*7;
    return b;
}

void full_test() {

    //////////////////////////////////// Setup ////////////////////////////////////////////////

    // message to encrypt/decrypt
    std::string message = random_string(255);

    // elgamal vars
    crtgamal_params_t params;
    crtgamal_key_t key, key_decoded;
    crtgamal_ciphertext_t cipher, cipher_after;
    bsgs_table_t table;
    // need to generate a random number between 0 and 2^32 - 1
    // pixel can handle larger numbers than samsung
    dig_t plain = large_rand(), res, res2; // rand_uint64() instead of 36435345 fails // numbers bigger than somewhere between 2^32 -1 and 2^33 - 1 fail
    unsigned char *buff;
    size_t size, size_ciphertext;

    crtgamal_init(CURVE_256_SEC); // try CURVE_256_SEC instead
    crt_params_create_default(params, DEFAULT_32_INTEGER_PARAMS);

    // sha vars
    unsigned char md[SHA256_DIGEST_LENGTH]; // 32 bytes
    std::array<std::uint8_t, 8> key_bytes;

    // aes vars
    unsigned char aes_key[AES_BLOCK_SIZE + 1];

    //////////////////////////////////// Encryption ////////////////////////////////////////////////

    crtgamal_generate_keys(key, params);

    // hash it -> symmetric key
    key_bytes = to_bytes(plain);
//    LOGW("%" PRIu64 "\n", plain);
//    LOGW("%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " ",
//            key_bytes[0], key_bytes[1], key_bytes[2], key_bytes[3], key_bytes[4], key_bytes[5], key_bytes[6], key_bytes[7]);

    if(!simpleSHA256(&key_bytes, 8, md)) {
        // handle error
        LOGW("error occured");
    }

    memcpy(aes_key, md, AES_BLOCK_SIZE);
    aes_key[AES_BLOCK_SIZE] = 0;

    // elgamal
    crtgamal_encrypt(cipher, key, plain);

    size_ciphertext = crt_get_encoded_ciphertext_size(cipher);
    buff = (unsigned char *) malloc(size_ciphertext);
    crt_encode_ciphertext(buff, (int) size_ciphertext, cipher);
    crt_decode_ciphertext(cipher_after, buff, (int) size_ciphertext);
    free(buff);

    gamal_init_bsgs_table(table, 1L << 8);

    // aes
    char *ct = do_aes_encrypt(aes_key, message);

    //////////////////////////////////// Decryption ////////////////////////////////////////////////

    std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();

    // elgamal
    crtgamal_decrypt(&res, key, cipher_after, table);

    // hash res -> aes key
    key_bytes = to_bytes(res);
//    LOGW("%" PRIu64 "\n", res);
//    LOGW("%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " " "%" PRIu8 " ",
//         key_bytes[0], key_bytes[1], key_bytes[2], key_bytes[3], key_bytes[4], key_bytes[5], key_bytes[6], key_bytes[7]);
    if(!simpleSHA256(&key_bytes, 8, md)) {
        // handle error
        LOGW("error occured");
    }

    memcpy(aes_key, md, AES_BLOCK_SIZE);
    aes_key[AES_BLOCK_SIZE] = 0;

    // aes
    std::string result = do_aes_decrypt(aes_key, ct);

    std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
    auto dec_time = std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count();

    LOGW("dec time: %lld", dec_time);

    //////////////////////////////////// Check ////////////////////////////////////////////////
    if (message.compare(result) == 0) {
        LOGW("hybrid works");
    }
//    LOGW("%s", message.c_str());
//    LOGW("%s", result.c_str());

    //////////////////////////////////// Cleanup ////////////////////////////////////////////////

    gamal_free_bsgs_table(table);
    crt_params_free(params);
    crtgamal_ciphertext_free(cipher);
    crtgamal_ciphertext_free(cipher_after);
    gamal_deinit();
}


/**
 * nativeEncrypt
 */
jstring JNI_CRYPTO(nativeEncrypt)(JNIEnv *env, jclass,
                                  jstring jKey, jstring jContent) {
    if (jKey == nullptr || jContent == nullptr) {
        return env->NewStringUTF("");
    }

    const char *key = env->GetStringUTFChars(jKey, nullptr);
    const char *content = env->GetStringUTFChars(jContent, nullptr);
    if (key == nullptr || content == nullptr) {
        return env->NewStringUTF("");
    }

    const vector<char> &chars = EncryptByPubkeyString(content, key);
    char *buffer = vector_to_p_char(chars);
    char *encode_result = base64Encode(buffer, chars.size(), false);

    delete[] key;
    delete[] content;
    delete[] buffer;

//    for (int i = 0; i < 1000; i++) {
//        elgamal();
//    }
//    for (int i = 0; i < 1000; i++) {
//        measure_aes();
//    }
    for (int i = 0; i < 1000; i++) {
        full_test();
    }

    // aes test
//    std::string original = "AAAAAAAAAAAAAAAAAAAA";
//    unsigned char k[AES_BLOCK_SIZE + 1] = {'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 0};
//
//    char* ct = do_aes_encrypt(k, original);
//
//    std::string result = do_aes_decrypt(k, ct);
//
//    if (original.compare(result) == 0) {
//        LOGW("aes works");
//    }

    return env->NewStringUTF(encode_result);
}

/**
 * nativeVerify
 */
jboolean JNI_CRYPTO (nativeVerify)(JNIEnv *env, jclass,
                                   jstring jKey, jstring jContent, jbyteArray jSignBytes) {
    if (jKey == nullptr || jContent == nullptr) {
        return false;
    }

    const char *key = env->GetStringUTFChars(jKey, nullptr);
    const char *content = env->GetStringUTFChars(jContent, nullptr);
    if (key == nullptr || content == nullptr) {
        return false;
    }

    char *signBytes = jByteArrayToChars(env, jSignBytes);
    jboolean result = VerifyRsaSignByString(signBytes, strlen(signBytes), key, content);

    delete[] key;
    delete[] content;
    delete[] signBytes;
    return result;
}

