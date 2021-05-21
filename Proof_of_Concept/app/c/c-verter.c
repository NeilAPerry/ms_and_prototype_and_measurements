#include <jni.h>

JNIEXPORT jdouble JNICALL
Java_com_wbrawner_cverter_ConversionHelper_celsiusToFahrenheit(
            JNIEnv* env,
                jclass classInstance,
                    jdouble celsius
        ) {
        return return celsius * 9/5 + 32;
}

JNIEXPORT jdouble JNICALL
Java_com_wbrawner_cverter_ConversionHelper_fahrenheitToCelsius(
            JNIEnv* env,
                jclass classInstance,
                    jdouble fahrenheit
        ) {
        return (fahrenheit - 32) * 5/9;
}
