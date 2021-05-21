package com.example.meshmessaging;

import com.example.meshmessaging.EncryptorAesGcm;
import com.example.meshmessaging.ElGamalCoder;
import com.example.meshmessaging.EncryptedPair;
import ch.ethz.dsg.ecelgamal.ECElGamal;

import android.bluetooth.BluetoothAdapter;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.util.TimingLogger;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import org.bouncycastle.crypto.ec.ECDecryptor;
import org.bouncycastle.crypto.ec.ECElGamalDecryptor;
import org.bouncycastle.crypto.ec.ECElGamalEncryptor;
import org.bouncycastle.crypto.ec.ECEncryptor;
import org.bouncycastle.crypto.ec.ECPair;
import org.bouncycastle.crypto.params.ECDomainParameters;
import org.bouncycastle.crypto.params.ECPrivateKeyParameters;
import org.bouncycastle.crypto.params.ECPublicKeyParameters;
import org.bouncycastle.crypto.params.ParametersWithRandom;
import org.bouncycastle.math.ec.ECCurve;
import org.bouncycastle.math.ec.ECConstants;
import org.bouncycastle.math.ec.ECPoint;
import org.bouncycastle.util.encoders.Hex;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.math.BigInteger;
import java.nio.charset.Charset;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Map;
import java.util.Random;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class FirstFragment extends Fragment {

    byte[] publicKey = {48, 119, 48, 80, 6, 6, 43, 14, 7, 2, 1, 1, 48, 70, 2, 33, 0, -80, 30, 49, -94, -85, -90, -99, -52, 119, -101, 74, -40, -71, 21, 3, -91, -5, -53, -9, 43, -121, 16, 21, -85, -5, -9, -123, 24, -67, -81, 61, 39, 2, 33, 0, -122, 34, -29, 35, -115, -46, -17, 16, -102, 71, 22, 6, 6, -46, 34, 93, 59, -44, 85, 59, 52, 114, -2, 105, 90, -57, 125, 126, -7, 18, 91, -14, 3, 35, 0, 2, 32, 44, -118, -86, -103, -55, -36, -93, -113, 71, 15, -104, 15, 49, -117, 61, 113, 77, 104, 63, 34, 40, -50, 13, -107, 99, -59, 64, -91, -107, 50, 86, 113};
    byte[] privateKey = {48, 121, 2, 1, 0, 48, 80, 6, 6, 43, 14, 7, 2, 1, 1, 48, 70, 2, 33, 0, -80, 30, 49, -94, -85, -90, -99, -52, 119, -101, 74, -40, -71, 21, 3, -91, -5, -53, -9, 43, -121, 16, 21, -85, -5, -9, -123, 24, -67, -81, 61, 39, 2, 33, 0, -122, 34, -29, 35, -115, -46, -17, 16, -102, 71, 22, 6, 6, -46, 34, 93, 59, -44, 85, 59, 52, 114, -2, 105, 90, -57, 125, 126, -7, 18, 91, -14, 4, 34, 2, 32, 26, 12, -30, 58, 29, -85, -3, 105, -126, 28, -19, -66, 83, -3, 62, 30, -4, 65, -65, 89, -57, 59, -88, -20, -52, 71, -75, 91, 85, 66, -110, -91};
    byte[] serializedMessage;

    public static EncryptedPair encrypt(String msg, byte[] publicKey) throws Exception {

//        TimingLogger timingLogger = new TimingLogger("encrypt", "");

        // create symmetric key
        SecretKey key = EncryptorAesGcm.newKey();

//        timingLogger.addSplit("aes keygen");

        // encrypt message symmetrically
        byte[] ct = EncryptorAesGcm.encrypt(msg, key);

        // encrypt symmetric key with elgamal
//        timingLogger.addSplit("aes encrypt");
        byte[] encodedKey = key.getEncoded();
        Log.d("mesh", "encoded key: " + Arrays.toString(encodedKey));
//        timingLogger.addSplit("get elgamal key");
        byte[] encryptedKey = ElGamalCoder.encyptByPublicKey(encodedKey, publicKey);
//        timingLogger.addSplit("elgamal encrypt");

//        timingLogger.dumpToLog();

        // return encrypted key and encrypted body
        EncryptedPair pair = new EncryptedPair(encryptedKey, ct);
        return pair;

    }

    public static String decrypt(byte[] privateKey, EncryptedPair pair) throws Exception {

        TimingLogger timingLogger = new TimingLogger("decrypt", "");

        // get encrypted key and encrypted body
        byte[] encryptedKey = pair.encryptedKey;
        byte[] ct = pair.ct;
        timingLogger.addSplit("unpack object");

        // decrypt key
        byte[] encodedKey = ElGamalCoder.decyptByPrivateKey(encryptedKey, privateKey);
        timingLogger.addSplit("elgamal decrypt");
        SecretKey key = new SecretKeySpec(encodedKey, 0, encodedKey.length, "AES");
        timingLogger.addSplit("decode aes key");

        // decrypt body
        String pt = EncryptorAesGcm.decrypt(ct, key);
        timingLogger.addSplit("aes decrypt");

        timingLogger.dumpToLog();

        return pt;

    }

    public void broadcast() {
        return;
    }

    private byte[][] buildMessages(byte[] msg) {
        // each message can only be 23 bytes => split into chunks of 22 bytes
        int size = msg.length;
        int chunks = (size / 22) + 1;
        Log.d("mesh", "chunks: " + String.valueOf(chunks));
//        byte[] msgBytes = msg.getBytes(Charset.forName( "UTF-8" ));
        byte[] msgBytes = msg;
        byte[][] result = new byte[chunks][23];
        boolean done = false;

        for (int i = 0; i < chunks; i++) {
            for (int j = 0; j < 23; j++) {
                if ((i * 22) + j - 1 == size) {
                    done = true;
                }
                if (done) {
                    continue;
                }
                if (j == 0) {
                    result[i][j] = (byte) i;
                } else {
//                    Log.d("mesh", "i is: " + String.valueOf((i)) + " and j is: " + String.valueOf((j)) + " and length is: " + String.valueOf((size)));
                    result[i][j] = msgBytes[(i * 22) + j - 1];
                }
            }
        }
        return result;
    }

    private byte[] decodeMessage(byte[][] msgsBytes) {
        Log.d("mesh", "decoding message");
        byte[] msg = new byte[22 * 11];
        byte[] msgBytesChunk = new byte[22];
        for (int i = 0; i < msgsBytes.length; i ++) {
            for (int j = 0; j < 22; j++) {
                msgBytesChunk[j] = msgsBytes[i][j + 1];
                msg[(i * 22) + j] = msgBytesChunk[j];
//                Log.d("mesh", String.valueOf((int) msgBytesChunk[j]));
            }
            try {
//                Log.d("mesh", "decoded message:");
//                Log.d("mesh", new String(msgBytesChunk, "UTF-8"));
            } catch (Exception e) {
                Log.d("mesh", "failed to decode message");
            }

        }

        return msg;

    }

    public byte[] readFile(String fileName) throws IOException {
        File path  = Environment.getExternalStorageDirectory();
        File file = new File(path, fileName);
        int size = (int) file.length();
        byte[] bytes = new byte[size];
        try {
            BufferedInputStream buf = new BufferedInputStream(new FileInputStream(file));
            buf.read(bytes, 0, bytes.length);
            buf.close();
        } catch (FileNotFoundException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return bytes;
    }

    @Override
    public View onCreateView(
            LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState
    ) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_first, container, false);
    }

    public void onViewCreated(@NonNull View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        view.findViewById(R.id.button_first).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "button clicked");
//                for (int i = 0; i < 1000; i++) {
                    try {

//                        // public
//                        byte[] publicKey;
//                        // private key
//                        byte[] privateKey;

                        // generate elgamal keys
                        Map<String, Object> keyMap = ElGamalCoder.initKey();
                        publicKey = ElGamalCoder.getPublicKey(keyMap);
                        privateKey = ElGamalCoder.getPrivateKey(keyMap);
//
//                        Log.d("mesh", "read: " + Arrays.toString(publicKey));
//                        Log.d("mesh", "read: " + Arrays.toString(privateKey));

                        // encrypt
                        EncryptedPair pair = FirstFragment.encrypt(randomString(10), publicKey); // 288

                        byte[] serializedPair = serialize(pair);
                        serializedMessage = serializedPair;
                        EncryptedPair deserializedPair = (EncryptedPair) deserialize(serializedPair);

                        // decrypt
                        String pt = FirstFragment.decrypt(privateKey, deserializedPair);
//                    String pt = FirstFragment.decrypt(privateKey, pair);

                        Log.d("mesh", pt);

                        Log.d("mesh", "Serialized size: " + String.valueOf(serialize(pair).length));


                    } catch (Exception e) {
                        Log.d("mesh", e.toString());
                        Log.d("mesh", "encrypt decrypt failed");
                    }

//                FirstFragmentDirections.ActionFirstFragmentToSecondFragment action =
//                        FirstFragmentDirections.
//                                actionFirstFragmentToSecondFragment("From FirstFragment");
//                NavHostFragment.findNavController(FirstFragment.this)
//                        .navigate(action);
                }
//            }
        });

        view.findViewById(R.id.button_advertise).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "advertise");
                // check if ble advertisements are supported
                if( !BluetoothAdapter.getDefaultAdapter().isMultipleAdvertisementSupported() ) {
                    Log.d("mesh", "Multiple advertisement not supported");
                }

//                String test = "This is a message that will be split up into pieces. It is more than 1 chunk long.";
//                String test = "Alternative message to see if swapping them out works. Hopefully it does... :)";
//                byte[][] msgsBytes = buildMessages(test);
                byte[][] msgsBytes = buildMessages(serializedMessage);

                BLE ble;
                byte[][] receivedMsgsBytes = new byte[11][23];

                for (int i = 0; i < msgsBytes.length; i++) {
                    try {
                        Log.d("mesh", "advertising: " + String.valueOf(i));
                        ble = new BLE(receivedMsgsBytes);
                        ble.advertise(msgsBytes[i]);
                        Thread.sleep(10000);
                    } catch (Exception e) {
                        Log.d("mesh", "advertising failed");
                    }

                }
            }
        });

        view.findViewById(R.id.button_discover).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try {
                    for (int i = 0; i < 11; i++) {
                        Log.d("mesh", "read: " + Arrays.toString(readFile(String.valueOf(i))));
                    }
                } catch (Exception e) {
                    Log.d("mesh", "read: " + "failed to read file");
                }

                byte[][] receivedMsgsBytes = new byte[11][23];
                int index;
                Log.d("mesh", "discover");
                BLE ble;
                for (int i = 0; i < 11; i++) {
                    try {
                        ble = new BLE(receivedMsgsBytes);
                        ble.discover();
//                        Thread.sleep(30000);
//                        while (!ble.finished) {;}
//                        Log.d("mesh", "found: " + Arrays.toString(ble.resultRow));
//                        Log.d("mesh", "found: " + Arrays.toString(receivedMsgsBytes[i]));
//                        index = (int) ble.resultRow[0];
//                        for (int j = 0; j < 23; j++) {
//                            receivedMsgsBytes[index][j] = ble.resultRow[j];
//                        }

                    } catch (Exception e) {
                        Log.d("mesh", "discovery failed");
                    }
                }
            }
        });

        view.findViewById(R.id.button_read_message).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                byte[][] receivedMsgsBytes = new byte[11][23];
                try {
//                    receivedMsgsBytes[0] = readFile("0");
//                    receivedMsgsBytes[1] = readFile("1");
//                    receivedMsgsBytes[2] = readFile("2");
//                    receivedMsgsBytes[3] = readFile("3");
//                    byte[] msgBytes = decodeMessage(receivedMsgsBytes);
//                    try {
//                        Log.d("mesh", new String(msgBytes, "UTF-8"));
//                    } catch (Exception e) {
//
//                    }

                    for (int i = 0; i < 11; i++) {
                        receivedMsgsBytes[i] = readFile(String.valueOf(i));
                    }
                    byte[] msgBytes = decodeMessage(receivedMsgsBytes);
                    byte[] shortenedMsg = new byte[225];
                    for (int i = 0; i < 225; i++) {
                        shortenedMsg[i] = msgBytes[i];
                    }
                    EncryptedPair deserializedPair = (EncryptedPair) deserialize(shortenedMsg);

                    // decrypt
                    String pt = FirstFragment.decrypt(privateKey, deserializedPair);
//                    String pt = FirstFragment.decrypt(privateKey, pair);

                    Log.d("mesh", pt);


//                    Log.d("mesh", "read: " + Arrays.toString(readFile("0")));
                } catch (Exception e) {
                    Log.d("mesh", "read: " + "failed to read file");
                }
            }
        });

        view.findViewById(R.id.button_pfelgamal).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "elgamal encrypt benchmark");
                TimingLogger timingLogger;
                String msg;
                byte[] encodedKey; // = {-98, 127, 17, -35, -98, 104, 68, 96, 126, -27, 108, 111, -78, -14, 6, -97, -2, 67, 11, 64, -20, 65, -11, -84, 69, 62, -58, 85, -75, 42, 72, -47};
                SecretKey key;
                byte[] encryptedKey;
                byte[] ct;
                String pt;

//                Log.d("mesh", String.valueOf(encodedKey.length));

                for (int i = 0; i < 1000; i++) {
                    try {
                        // gen message
                        msg = randomString(288);
                        // gen key
                        encodedKey = randomByteArray(32);

//                        timingLogger = new TimingLogger("encrypt", "");
//                        byte[] encryptedKey = ElGamalCoder.encyptByPublicKey(encodedKey, publicKey);
//                        timingLogger.dumpToLog();
//
//                        timingLogger = new TimingLogger("decrypt", "");
//                        encodedKey = ElGamalCoder.decyptByPrivateKey(encryptedKey, privateKey);
//                        timingLogger.dumpToLog();





                        // encrypt
//                        timingLogger = new TimingLogger("encrypt", "");

                        // get aes key
                        key = new SecretKeySpec(encodedKey, 0, encodedKey.length, "AES");
//                        timingLogger.addSplit("decode aes key");

                        // encrypt message symmetrically
                        long start =  System.nanoTime();
                        ct = EncryptorAesGcm.encrypt(msg, key);
                        long end = System.nanoTime();
                        Log.d("mesh", String.valueOf(end - start));
//                        timingLogger.addSplit("aes encrypt");

                        // encrypt symmetric key with elgamal
                        encodedKey = key.getEncoded();
//                        timingLogger.addSplit("get encoded key");
                        encryptedKey = ElGamalCoder.encyptByPublicKey(encodedKey, publicKey);
//                        timingLogger.addSplit("elgamal encrypt");

//                        timingLogger.dumpToLog();

                        // decrypt
//                        timingLogger = new TimingLogger("decrypt", "");

                        // decrypt key
                        encodedKey = ElGamalCoder.decyptByPrivateKey(encryptedKey, privateKey);
//                        timingLogger.addSplit("elgamal decrypt");
                        key = new SecretKeySpec(encodedKey, 0, encodedKey.length, "AES");
//                        timingLogger.addSplit("decode aes key");

                        // decrypt body
                        pt = EncryptorAesGcm.decrypt(ct, key);
//                        timingLogger.addSplit("aes decrypt");

//                        timingLogger.dumpToLog();

                    } catch (Exception e) {
                        Log.d("mesh", "elgamal encrypt failed");
                    }
                }
            }
        });

        view.findViewById(R.id.button_ecelgamal_bc).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "elgamal decrypt benchmark");
                long start;
                long end;

                BigInteger n = new BigInteger("6277101735386680763835789423176059013767194773182842284081");
                ECCurve.Fp curve = new ECCurve.Fp(
                        new BigInteger("6277101735386680763835789423207666416083908700390324961279"), // q
                        new BigInteger("fffffffffffffffffffffffffffffffefffffffffffffffc", 16), // a
                        new BigInteger("64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1", 16), // b
                        n, ECConstants.ONE);
                ECDomainParameters params = new ECDomainParameters(
                        curve,
                        curve.decodePoint(Hex.decode("03188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012")), // G
                        n);
                ECPublicKeyParameters pubKey = new ECPublicKeyParameters(
                        curve.decodePoint(Hex.decode("0262b12d60690cdcf330babab6e69763b471f994dd702d16a5")), // Q
                        params);
                ECPrivateKeyParameters priKey = new ECPrivateKeyParameters(
                        new BigInteger("651056770906015076056810763456358567190100156695615665659"), // d
                        params);
                ParametersWithRandom pRandom = new ParametersWithRandom(pubKey, new SecureRandom());

                // setup encryptor
                ECEncryptor encryptor = new ECElGamalEncryptor();
                encryptor.init(pRandom);

                // set up decryptor
                ECDecryptor decryptor = new ECElGamalDecryptor();
                decryptor.init(priKey);

                for (int i = 0; i < 10; i++) {
                    byte[] encodedKey = randomByteArray(32);
                    BigInteger value = new BigInteger(encodedKey);

//                start =  System.nanoTime();
                    ECPair pair = ElGamalCoder.ecencrypt(encryptor, priKey, value);
//                end = System.nanoTime();
//                Log.d("mesh", "ec encrypt: " + String.valueOf(end - start));

//                start =  System.nanoTime();
                    TimingLogger timingLogger = new TimingLogger("decrypt", "");
                    ECPoint point = ElGamalCoder.ecdecrypt(decryptor, pair);
                    timingLogger.addSplit("elgamal decrypt");
                    timingLogger.dumpToLog();
//                end = System.nanoTime();
//                Log.d("mesh", "ec decrypt: " + String.valueOf(end - start));

                    if (priKey.getParameters().getG().multiply(value).equals(point)) {
                        Log.d("mesh", "EC Elgamal works");
                    }

                }

            }
        });

        view.findViewById(R.id.button_ecelgamal_n).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "ec elgamal n benchmark");

                CustomEC ec = new CustomEC();

            }
        });

        view.findViewById(R.id.button_ecelgamal_c).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Log.d("mesh", "elgamal c benchmark");

                ECElGamal.CRTParams params32 = ECElGamal.getDefault32BitParams();
                ECElGamal.ECElGamalKey key32 = ECElGamal.generateNewKey(params32);
                ECElGamal.ECElGamalCiphertext cipher1,cipher2;
                int val1 = 2, val2 = -3;
                cipher1 = ECElGamal.encrypt(BigInteger.valueOf(val1), key32);
                cipher2 = ECElGamal.encrypt(BigInteger.valueOf(val2), key32);
                cipher1 = ECElGamal.add(cipher1, cipher2);
                int decriptedVal = ECElGamal.decrypt32(cipher1, key32);
                if (val1 + val2 == decriptedVal) {
                    Log.d("mesh", "elgamal c worked");
                }

            }
        });
    }

    private byte[] serialize(Object object) throws IOException {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             ObjectOutputStream out = new ObjectOutputStream(bos)) {
            out.writeObject(object);
            return bos.toByteArray();
        }
    }

    private Object deserialize(byte[] bytes) throws IOException, ClassNotFoundException {
        try (ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
             ObjectInputStream in = new ObjectInputStream(bis)) {
            return in.readObject();
        }
    }

    public String randomString(int length) {

        int leftLimit = 97; // letter 'a'
        int rightLimit = 122; // letter 'z'
        int targetStringLength = length;
        Random random = new Random();
        StringBuilder buffer = new StringBuilder(targetStringLength);
        for (int i = 0; i < targetStringLength; i++) {
            int randomLimitedInt = leftLimit + (int)
                    (random.nextFloat() * (rightLimit - leftLimit + 1));
            buffer.append((char) randomLimitedInt);
        }
        String generatedString = buffer.toString();

        return generatedString;
    }

    public byte[] randomByteArray(int length) {

        int leftLimit = 0; // letter 'a'
        int rightLimit = 255; // letter 'z'
        int targetLength = length;
        Random random = new Random();
        byte[] buffer = new byte[targetLength];
        for (int i = 0; i < targetLength; i++) {
            int randomLimitedInt = leftLimit + (int)
                    (random.nextFloat() * (rightLimit - leftLimit + 1));
            buffer[i] = (byte) randomLimitedInt;
        }

        return buffer;
    }
}
