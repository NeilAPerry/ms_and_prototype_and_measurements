package com.example.meshmessaging;

import java.security.spec.ECPoint;

public class ECElGamalPair {
    public ECPoint first;
    public ECPoint second;

    public ECElGamalPair(ECPoint first, ECPoint second) {
        this.first = first;
        this.second = second;
    }
}
