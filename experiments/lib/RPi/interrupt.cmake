target_sources(${LF_MAIN_TARGET} PRIVATE 
    interrupt.c
)

target_link_libraries(
    ${LF_MAIN_TARGET} PRIVATE -lwiringPi
)