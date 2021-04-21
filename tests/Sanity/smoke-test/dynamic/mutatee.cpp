#include <cstdio>
#include <unistd.h>
#include <cstdlib>

using namespace std;

int a = 0;

void incr(void)
{
	a++;
}

int function_name(void)
{
	fprintf(stderr, "FUNCTION EXECUTED. VALUE = %i\n", a);
}

int main(int argc, char **argv)
{
	int n = 10, i;
	FILE *f = fopen("RESULT.log", "w");
	if(argc > 1)
	{
		if((n = atoi(argv[1])) <= 0)
			n = 10;
	}
	else
		n = 10;
	
	for(i = 0; i < n; i++)
	{
		function_name();
		sleep(3);
	}
	
	if(a)
		fprintf(f, "MUTATION OK.\n");
	else
		fprintf(f, "MUTATION FAILED.\n");

	fclose(f);
	return !a;
}
