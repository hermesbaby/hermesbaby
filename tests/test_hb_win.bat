## TEST_01: Home Screen
cd ./dist/hb-dist/
time ./hb


## TEST_02: new
mkdir test_new
cd test_new
time ../hb new --template zero .


## TEST_03: html
time ../hb html

## TEST_04: configure
../hb configure

## TEST_05: html-live
../hb html-live
