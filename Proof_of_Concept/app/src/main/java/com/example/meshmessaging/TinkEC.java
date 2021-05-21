package com.example.meshmessaging;

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Log;

import java.math.BigInteger;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.Provider;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.Security;
import java.security.interfaces.ECPrivateKey;
import java.security.interfaces.ECPublicKey;
import java.security.spec.ECGenParameterSpec;
import java.security.spec.ECParameterSpec;
import java.security.spec.ECPoint;
import java.security.spec.EllipticCurve;
import java.security.spec.ECFieldFp;

public class TinkEC {

    ECGenParameterSpec ecsp;
    KeyPair kp;
    PublicKey pubKey;
    PrivateKey privKey;
    ECPublicKey ecPublicKey;
    ECPrivateKey ecPrivateKey;
    ECParameterSpec ecParameterSpec;
    EllipticCurve curve;
    static final BigInteger ONE = new BigInteger("1");;
    static final BigInteger TWO = new BigInteger("2");
    static final BigInteger NEGATIVE_ONE = new BigInteger("-1");
    BigInteger a;
    BigInteger b;
    BigInteger n;
    BigInteger p;
    ECPoint G;

    byte[] randomness;
    SecureRandom random;

    public TinkEC() {

        // List all security providers
//        for (Provider p : Security.getProviders()) {
//            Log.d("mesh", String.format("== %s ==", p.getName()));
//            for (Provider.Service s : p.getServices()) {
//                Log.d("mesh", String.format("- %s", s.getAlgorithm()));
//            }
//        }

        try {
            KeyPairGenerator kpg;
            kpg = KeyPairGenerator.getInstance("EC","AndroidOpenSSL");
            ECGenParameterSpec ecsp;
            this.ecsp = new ECGenParameterSpec("secp256r1");
            kpg.initialize(this.ecsp);

            this.kp = kpg.genKeyPair();
            this.privKey = kp.getPrivate();
            this.pubKey = kp.getPublic();

            Log.d("mesh", this.privKey.toString());
            Log.d("mesh", this.pubKey.toString());

            this.ecPublicKey = (ECPublicKey) kp.getPublic();
            this.ecPrivateKey = (ECPrivateKey) kp.getPrivate();
            this.ecParameterSpec = ecPublicKey.getParams();
            this.curve = ecParameterSpec.getCurve();

            this.a = curve.getA();
            this.b = curve.getB();
            this.p = ((ECFieldFp) curve.getField()).getP();
            this.n = this.ecParameterSpec.getOrder();

            this.G = this.ecParameterSpec.getGenerator(); // is this P from pk = xP? | yes, G = P

            this.random = new SecureRandom();
            this.randomness = new byte[64];

            long start;
            long end;

            for (int i = 0; i < 1000; i++) {

                random.nextBytes(randomness);
                BigInteger r = new BigInteger(randomness);

                ECPoint msg = scalmult(this.G, r);

                start = System.nanoTime();
                ECElGamalPair ct = elgamalEncrypt(msg);
                end = System.nanoTime();
                Log.d("mesh", "ec encrypt: " + String.valueOf((end - start) / 1000000));

                start = System.nanoTime();
                ECPoint pt = elgamalDecrypt(ct);
                end = System.nanoTime();
                Log.d("mesh", "ec decrypt: " + String.valueOf((end - start) / 1000000));

                if (!msg.equals(pt)) {
                    Log.d("mesh", "elgamal failed");
                }
            }

        } catch (Exception e) {
            Log.d("mesh", "CustomEC failed", e);
        }

    }

    public ECElGamalPair elgamalEncrypt(ECPoint p_m) throws Exception {

        random.nextBytes(randomness);
        BigInteger r = new BigInteger(randomness);

        ECPoint C = scalmult(this.G, r);
        ECPoint C_prime = scalmult(C, this.ecPrivateKey.getS()); // trying to get x

        ECElGamalPair pair = new ECElGamalPair(C, addPoint(C_prime, p_m));

        if (!checkOnCurve(scalmult(this.G, this.ecPrivateKey.getS()))) { // check that pub key is on curve
            throw new Exception("invalid point");
        }

        return pair;
    }

    public ECPoint elgamalDecrypt(ECElGamalPair pair) throws Exception{

        ECPoint C_prime = scalmult(pair.first, this.ecPrivateKey.getS()); // trying to get x
        ECPoint Neg_C_prime = new ECPoint(C_prime.getAffineX(), C_prime.getAffineY().multiply(NEGATIVE_ONE));
        ECPoint p_m = addPoint(pair.second, Neg_C_prime);

        if (!checkOnCurve(pair.first) || !checkOnCurve(pair.second) || !checkOnCurve(p_m)) {
            throw new Exception("invalid point");
        }

        return p_m;
    }

    public boolean checkOnCurve(ECPoint point) {
        BigInteger x = point.getAffineX();
        BigInteger y = point.getAffineY();
        BigInteger y_2 = y.multiply(y);
        BigInteger x_3 = x.multiply(x).multiply(x);
        BigInteger ax = this.a.multiply(x);
        return y_2.mod(p).equals(x_3.add(ax).add(this.b).mod(p));
    }

    public ECPoint scalmult(ECPoint P, BigInteger kin){
        ECPoint R = ECPoint.POINT_INFINITY,S = P;
        BigInteger k = kin.mod(p);
        int length = k.bitLength();
        //System.out.println("length is" + length);
        byte[] binarray = new byte[length];
        for(int i=0;i<=length-1;i++){
            binarray[i] = k.mod(TWO).byteValue();
            k = k.divide(TWO);
        }

        for(int i = length-1;i >= 0;i--){
            // i should start at length-1 not -2 because the MSB of binarry may not be 1
            R = doublePoint(R);
            if(binarray[i]== 1)
                R = addPoint(R, S);
        }
        return R;
    }

    public ECPoint addPoint(ECPoint r, ECPoint s) {

        if (r.equals(s))
            return doublePoint(r);
        else if (r.equals(ECPoint.POINT_INFINITY))
            return s;
        else if (s.equals(ECPoint.POINT_INFINITY))
            return r;
        BigInteger slope = (r.getAffineY().subtract(s.getAffineY())).multiply(r.getAffineX().subtract(s.getAffineX()).modInverse(p)).mod(p);
        BigInteger Xout = (slope.modPow(TWO, p).subtract(r.getAffineX())).subtract(s.getAffineX()).mod(p);
        BigInteger Yout = s.getAffineY().negate().mod(p);
        Yout = Yout.add(slope.multiply(s.getAffineX().subtract(Xout))).mod(p);
        ECPoint out = new ECPoint(Xout, Yout);
        return out;
    }

    public ECPoint doublePoint(ECPoint r) {
        if (r.equals(ECPoint.POINT_INFINITY))
            return r;
        BigInteger slope = (r.getAffineX().pow(2)).multiply(new BigInteger("3"));
        slope = slope.add(a);
        slope = slope.multiply((r.getAffineY().multiply(TWO)).modInverse(p));
        BigInteger Xout = slope.pow(2).subtract(r.getAffineX().multiply(TWO)).mod(p);
        BigInteger Yout = (r.getAffineY().negate()).add(slope.multiply(r.getAffineX().subtract(Xout))).mod(p);
        ECPoint out = new ECPoint(Xout, Yout);
        return out;
    }

}