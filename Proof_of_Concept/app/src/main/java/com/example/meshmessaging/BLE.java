package com.example.meshmessaging;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.le.AdvertiseCallback;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertiseSettings;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.os.Environment;
import android.os.Handler;
import android.os.ParcelUuid;
import android.text.TextUtils;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.lang.reflect.Method;
import android.bluetooth.BluetoothGatt;

public class BLE {

    BluetoothLeAdvertiser advertiser;
    AdvertiseSettings adsettings;
    AdvertiseCallback advertisingCallback;
    ParcelUuid pUuid;

    BluetoothLeScanner mBluetoothLeScanner;
    Handler mHandler;
    ScanCallback mScanCallback;
    ArrayList<ScanFilter> filters;
    ScanSettings scsettings;

    byte[][] receivedMsgsBytes;
    boolean[] receivedRows = {false, false, false, false};
    byte[] resultRow;
    boolean finished = false;

    public BLE(byte[][] receivedMsgsBytes) {
        this.receivedMsgsBytes = receivedMsgsBytes;
        this.advertiseSetUp();;
        this.discoverSetUp();
    }

    private void advertiseSetUp() {
        this.advertiser = BluetoothAdapter.getDefaultAdapter().getBluetoothLeAdvertiser();

        this.adsettings = new AdvertiseSettings.Builder()
                .setAdvertiseMode( AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY )
//                .setTxPowerLevel( AdvertiseSettings.ADVERTISE_TX_POWER_HIGH )
                .setTxPowerLevel( AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM )
//                .setTxPowerLevel( AdvertiseSettings.ADVERTISE_TX_POWER_LOW )
//                .setTxPowerLevel( AdvertiseSettings.ADVERTISE_TX_POWER_ULTRA_LOW )
                .setConnectable( false )
                .build();

        this.pUuid = new ParcelUuid( UUID.fromString( "0000ff01-0000-1000-8000-00805F9B34FB" ) );



        this.advertisingCallback = new AdvertiseCallback() {
            @Override
            public void onStartSuccess(AdvertiseSettings settingsInEffect) {
                super.onStartSuccess(settingsInEffect);
            }

            @Override
            public void onStartFailure(int errorCode) {
                Log.e( "BLE", "Advertising onStartFailure: " + errorCode );
                super.onStartFailure(errorCode);
            }
        };
    }

    private void discoverSetUp() {
//        this.receivedMsgsBytes = new byte[4][23];
        this.resultRow = new byte[23];
        this.filters = new ArrayList<>();
        this.mHandler = new Handler();
        this.mScanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                Log.d("mesh", "in onScanResult");
                super.onScanResult(callbackType, result);
                if( result == null)
//                        || result.getDevice() == null
//                        || TextUtils.isEmpty(result.getDevice().getName()) )
                    return;
                if (result.getDevice() == null) {
                    Log.d("mesh", "scan results: " + "null device");
                    Log.d("mesh", result.toString());
                    return;
                }
                if (TextUtils.isEmpty(result.getDevice().getName())) {
//                    Log.d("mesh", "scan results: " + "no device name");
//                    Log.d("mesh", result.toString());

                    // our message
                    // .get("0000ff01-0000-1000-8000-00805f9b34fb")
                    byte[] row = result.getScanRecord().getServiceData().get(new ParcelUuid(UUID.fromString( "0000ff01-0000-1000-8000-00805F9B34FB" )));
                    resultRow = row;
                    finished = true;
                    try {
                        Log.d("mesh", "scanned index: " + String.valueOf(resultRow[0]));
                        writeToFile(resultRow, String.valueOf(resultRow[0]));
                    } catch (Exception e) {

                    }

                    int index = (int) row[0];
//                    receivedRows[index] = true;
                    for (int i = 0; i < 23; i ++) {
                        receivedMsgsBytes[index][i] = row[i];
                    }

//                    if (receivedRows[0] && receivedRows[1] && receivedRows[2] && receivedRows[3]) {
////                        decodeMessage(receivedMsgsBytes);
//                    }

                    try {
//                        Log.d("mesh", new String(row, "UTF-8"));
                    } catch (Exception e) {

                    }

//                    Log.d("mesh", result.getScanRecord().getServiceData().get(new ParcelUuid(UUID.fromString( "0000ff01-0000-1000-8000-00805F9B34FB" ))).toString()); // i think this has one row of the byte array - collect all 4 - need to call code to advertise each row
//                    Log.d("mesh", new String(result.getScanRecord().getServiceData(), "UTF-8"));
                    // collect the 4 and store them in receivedMsgsBytes in sorted order, then display it
//                    receivedMsgsBytes[]
                    return;
                }


                StringBuilder builder = new StringBuilder( result.getDevice().getName() );

//                builder.append("\n").append(new String(result.getScanRecord().getServiceData(result.getScanRecord().getServiceUuids().get(0)), Charset.forName("UTF-8")));
//                builder.append("\n").append(new String(result.getScanRecord().getServiceData(result.getScanRecord().getServiceUuids().get(0)), Charset.forName("UTF-8")));

                // pixel ac:37:43:83:b7:cf - AC:37:43:83:B7:CF --- mDevice: changes each time
                // samsung b8:6c:e8:2a:81:63 - B8:6C:E8:2A:81:63
                // [68, 97, 116, 97]
//                Log.d("mesh", "scan results: " + builder.toString());
//                Log.d("mesh", "scan results: " + result.toString());
            }

            @Override
            public void onBatchScanResults(List<ScanResult> results) {
                super.onBatchScanResults(results);
            }

            @Override
            public void onScanFailed(int errorCode) {
                Log.e( "BLE", "Discovery onScanFailed: " + errorCode );
                super.onScanFailed(errorCode);
            }
        };

        this.mBluetoothLeScanner = BluetoothAdapter.getDefaultAdapter().getBluetoothLeScanner();
        ScanFilter filter = new ScanFilter.Builder()
                .setServiceUuid( new ParcelUuid(UUID.fromString( "0000ff01-0000-1000-8000-00805F9B34FB" ) ) )
                .build();
        this.filters.add( filter );
        this.scsettings = new ScanSettings.Builder()
                .setScanMode( ScanSettings.SCAN_MODE_LOW_LATENCY )
                .build();

        this.mHandler.postDelayed(new Runnable() {
            @Override
            public void run() {
                mBluetoothLeScanner.stopScan(mScanCallback);
            }
        }, 10000);
    }

    public void advertise(byte[] dataBytes) {
        AdvertiseData data = new AdvertiseData.Builder()
                .setIncludeDeviceName( false )
                .addServiceUuid( this.pUuid )
                .addServiceData( this.pUuid, dataBytes )
                .build();

//        Log.d("mesh", data.toString());
//        Log.d("mesh", this.pUuid.toString());
        this.advertiser.startAdvertising( this.adsettings, data, this.advertisingCallback );

    }

    public void discover() {
        mBluetoothLeScanner.startScan(this.filters, this.scsettings, this.mScanCallback);
    }

    public void writeToFile(byte[] data, String fileName) throws IOException{
        File path  = Environment.getExternalStorageDirectory();
        FileOutputStream out = new FileOutputStream(path.getAbsolutePath() + "/" + fileName);
        out.write(data);
        out.close();
    }




}
