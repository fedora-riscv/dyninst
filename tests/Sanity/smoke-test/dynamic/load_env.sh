DYNINSTAPI_RT_LIB=/opt/rh/devtoolset-3/root/usr/lib64/dyninst/libdyninstAPI_RT.so
export DYNINSTAPI_RT_LIB
if [[ ! $LD_LIBRARY_PATH =~ .*dyninst.* ]]; then
	LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$LD_LIBRARY_PATH/dyninst
fi
export LD_LIBRARY_PATH
