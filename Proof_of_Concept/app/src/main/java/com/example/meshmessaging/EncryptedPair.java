package com.example.meshmessaging;

import java.io.Serializable;

public class EncryptedPair implements Serializable {

    public byte[] encryptedKey;
    public byte[] ct;

    public EncryptedPair(byte[] encryptedKey, byte[] ct) {
        this.encryptedKey = encryptedKey;
        this.ct = ct;
    }
}
