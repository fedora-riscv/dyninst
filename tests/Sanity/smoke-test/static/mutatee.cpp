#include <cstdio>
#include <unistd.h>
#include <cstdlib>
#include <iostream>

using namespace std;

int a = 0;

void incr(void)
{
	a++;
}

int function_name(void)
{
	int i;

	sleep(3);	
	
	if(a)
		printf("MUTATION OK.\n");
	else
		printf("MUTATION FAILED.\n");

	return a;
}

int main(int argc, char **argv)
{
	function_name();
}
