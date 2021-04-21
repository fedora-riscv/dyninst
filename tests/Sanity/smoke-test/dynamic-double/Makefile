CPP=g++
#DYNINST_ROOT=/opt/rh/devtoolset-2/root/usr/lib$(BITS)/dyninst
LINK=-L/opt/rh/devtoolset-3/root/usr/lib$(BITS)/dyninst -L/opt/rh/devtoolset-3/root/usr/lib$(BITS)/dyninst/lib
# -ldyninstAPI -ldynC -ldl
#LINK=-L/opt/rh/devtoolset-2/root/usr/lib$(BITS)/dyninst -L/opt/rh/devtoolset-2/root/usr/lib$(BITS)/dyninst/lib -ldyninstAPI -ldl

INCLUDE=-I/opt/rh/devtoolset-3/root/usr/include/dyninst
LINK2=-ldyninstAPI -ldl -lboost_system

all:	mutatee mutator

clean:
	rm mutatee mutator

mutatee:	mutatee.cpp
	$(CPP) -g -o mutatee mutatee.cpp

mutator:	mutator.cpp
	$(CPP) -g -o mutator $(INCLUDE) $(LINK) $(LINK2) mutator.cpp
