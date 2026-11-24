set(PYFMI_CSV_RUNTIME_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)
set(PYFMI_CSV_FMI_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/3rd_party/fmi_2/headers)

option(PYFMI_CSV_STATIC_STDLIB "Link the FMU shared library with static libstdc++/libgcc when supported" ON)

add_library(pyfmi_csv_runtime_core STATIC
    src/fmu_runtime_core.cpp
    src/fmu_runtime_csv.cpp
    src/fmu_runtime_values.cpp
)

target_include_directories(pyfmi_csv_runtime_core
    PUBLIC
        ${PYFMI_CSV_RUNTIME_INCLUDE_DIR}
)

target_compile_features(pyfmi_csv_runtime_core PUBLIC cxx_std_17)
set_target_properties(pyfmi_csv_runtime_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

add_library(pyfmi_csv_fmi2_cs SHARED
    src/fmi2_cs_api.cpp
)

target_include_directories(pyfmi_csv_fmi2_cs
    PUBLIC
        ${PYFMI_CSV_RUNTIME_INCLUDE_DIR}
        ${PYFMI_CSV_FMI_INCLUDE_DIR}
)

target_link_libraries(pyfmi_csv_fmi2_cs
    PRIVATE
        pyfmi_csv_runtime_core
)

target_compile_features(pyfmi_csv_fmi2_cs PUBLIC cxx_std_17)

# The runtime is consumed from build/runtime/ regardless of where its sources
# live in the tree.
set_target_properties(pyfmi_csv_fmi2_cs PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/runtime
    RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/runtime
)

if(PYFMI_CSV_STATIC_STDLIB)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        target_link_options(pyfmi_csv_fmi2_cs PRIVATE -static-libstdc++ -static-libgcc)
    endif()
endif()

if(BUILD_TESTING AND PYFMI_CSV_BUILD_TESTS)
    add_executable(pyfmi_csv_runtime_smoke_test
        tests/test_runtime_smoke.cpp
    )

    target_link_libraries(pyfmi_csv_runtime_smoke_test
        PRIVATE
            pyfmi_csv_runtime_core
    )

    target_include_directories(pyfmi_csv_runtime_smoke_test
        PRIVATE
            ${PYFMI_CSV_RUNTIME_INCLUDE_DIR}
    )

    add_test(
        NAME pyfmi_csv_runtime_smoke_test
        COMMAND pyfmi_csv_runtime_smoke_test
    )

    add_executable(pyfmi_csv_fmi2_api_smoke_test
        tests/test_fmi2_api_smoke.cpp
    )

    target_link_libraries(pyfmi_csv_fmi2_api_smoke_test
        PRIVATE
            pyfmi_csv_fmi2_cs
    )

    target_include_directories(pyfmi_csv_fmi2_api_smoke_test
        PRIVATE
            ${PYFMI_CSV_RUNTIME_INCLUDE_DIR}
            ${PYFMI_CSV_FMI_INCLUDE_DIR}
    )

    add_test(
        NAME pyfmi_csv_fmi2_api_smoke_test
        COMMAND pyfmi_csv_fmi2_api_smoke_test
    )
endif()
