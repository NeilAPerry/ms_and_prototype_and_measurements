package com.example.meshmessaging;

import android.util.Log;

import java.math.BigInteger;
import java.security.AlgorithmParameterGenerator;
import java.security.AlgorithmParameters;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.Security;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.Cipher;

import org.bouncycastle.crypto.ec.ECDecryptor;
import org.bouncycastle.crypto.ec.ECElGamalDecryptor;
import org.bouncycastle.crypto.ec.ECElGamalEncryptor;
import org.bouncycastle.crypto.ec.ECEncryptor;
import org.bouncycastle.crypto.ec.ECPair;
import org.bouncycastle.crypto.params.ECPrivateKeyParameters;
import org.bouncycastle.crypto.params.ParametersWithRandom;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.jce.spec.ElGamalParameterSpec;
import org.bouncycastle.math.ec.ECPoint;

/**
 * ElGamal coding components <br>
 * Jdk does not support the Bouncy Castle Support
 *
 * @author shaozuo
 * @date 2018/08/01
 */
public final class ElGamalCoder {

    public static final String ALGORITHM_NAME = "ElGamal";

    private ElGamalCoder() {

    }

    static {
        Security.addProvider(new BouncyCastleProvider());
    }

    private static final int KEY_SIZE = 256;
    private static final String PUBLIC_KEY = "public_key";
    private static final String PRIVATE_KEY = "private_key";

    /**
     * Public Key Initialization
     *
     * @Return Map Key map
     * @throws Exception
     */
    public static Map<String, Object> initKey() throws Exception {

        BouncyCastleProvider bcprov = new BouncyCastleProvider();

        AlgorithmParameterGenerator parameterGenerator = AlgorithmParameterGenerator
                .getInstance(ALGORITHM_NAME, bcprov);
        parameterGenerator.init(KEY_SIZE);

        AlgorithmParameters parameters = parameterGenerator.generateParameters();

        ElGamalParameterSpec spec = parameters.getParameterSpec(ElGamalParameterSpec.class);
        Log.d("mesh", "p: " + String.valueOf(spec.getP()));

        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(ALGORITHM_NAME, bcprov);
        keyPairGenerator.initialize(spec, new SecureRandom());

        KeyPair keyPair = keyPairGenerator.generateKeyPair();
        PublicKey publicKey = keyPair.getPublic();
        PrivateKey privateKey = keyPair.getPrivate();

        Map<String, Object> keyMap = new HashMap<>();
        keyMap.put(PUBLIC_KEY, publicKey);
        keyMap.put(PRIVATE_KEY, privateKey);
        return keyMap;
    }

    public static byte[] getPrivateKey(Map<String, Object> keyMap) {
        Key key = (Key) keyMap.get(PRIVATE_KEY);
        return key.getEncoded();
    }

    public static byte[] getPublicKey(Map<String, Object> keyMap) {
        Key key = (Key) keyMap.get(PUBLIC_KEY);
        return key.getEncoded();
    }

    /**
     * Use the public key to encrypt data
     *
     * @param data
     * Data to be encrypted
     * @param encodedPublicKey
     * Public Key
     * @return
     * @throws GeneralSecurityException
     */
    public static byte[] encyptByPublicKey(byte[] data, byte[] encodedPublicKey)
            throws GeneralSecurityException {

        BouncyCastleProvider bcprov = new BouncyCastleProvider();

        X509EncodedKeySpec encodedKeySpec = new X509EncodedKeySpec(encodedPublicKey);
        KeyFactory factory = KeyFactory.getInstance(ALGORITHM_NAME, bcprov);
        PublicKey publicKey = factory.generatePublic(encodedKeySpec);

        Cipher cipher = Cipher.getInstance(factory.getAlgorithm(), bcprov);

        cipher.init(Cipher.ENCRYPT_MODE, publicKey);
        System.out.println(data.length);
        return cipher.doFinal(data);
    }

    /**
     * Using the private key to decrypt the data
     *
     * @param data
     * Data to be decrypted
     * @param encodedPrivateKey
     * Private
     * @return
     * @throws GeneralSecurityException
     */
    public static byte[] decyptByPrivateKey(byte[] data, byte[] encodedPrivateKey)
            throws GeneralSecurityException {
        BouncyCastleProvider bcprov = new BouncyCastleProvider();

        PKCS8EncodedKeySpec encodedKeySpec = new PKCS8EncodedKeySpec(encodedPrivateKey);
        KeyFactory factory = KeyFactory.getInstance(ALGORITHM_NAME, bcprov);
        PrivateKey privateKey = factory.generatePrivate(encodedKeySpec);

        Cipher cipher = Cipher.getInstance(factory.getAlgorithm(), bcprov);
        cipher.init(Cipher.DECRYPT_MODE, privateKey);
        return cipher.doFinal(data);
    }

    public static ECPair ecencrypt(ECEncryptor encryptor, ECPrivateKeyParameters priKey, BigInteger value) {
        ECPoint data = priKey.getParameters().getG().multiply(value);
        ECPair pair = encryptor.encrypt(data);
        return pair;
    }

    public static ECPoint ecdecrypt(ECDecryptor decryptor, ECPair pair) {
        ECPoint result = decryptor.decrypt(pair);
        return result;
    }

}