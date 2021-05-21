# Set the minimum required version for cmake
cmake_minimum_required(VERSION 3.4.1)

# Define our native library
add_library(
            c-verter
            SHARED
            c-verter.c )

# Include the Android logging library for native code
find_library(
            log-lib
            log )

# Link our library with the Android logging library
target_link_libraries(
                    c-verters
                    ${log-lib} )
