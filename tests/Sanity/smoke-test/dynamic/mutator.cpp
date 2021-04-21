#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <iostream>

// dyninst libraries

#include "BPatch.h"
#include "BPatch_addressSpace.h"
#include "BPatch_process.h"
#include "BPatch_function.h"
#include "BPatch_point.h"
//#include "BPatch_flowGraph.h"

using namespace std;


BPatch bpatch;


int main(int argc, char **argv)
{
	int pid;
	BPatch_process *app_proc;
	BPatch_addressSpace *aspace;
	BPatch_image *image;

	// check the options
	if(argc != 2)
	{
		cerr << "ERROR ## Missing command line args. Use PID of the process you want to attach.\n";
		return 1;
	}

	pid = atoi(argv[1]);
	if(pid == 0)
	{
		cerr << "ERROR ## Wrong PID " << pid << ", please use another.\n";
		return 2;
	}

	// let's go...
	app_proc = bpatch.processAttach(NULL, pid);
	aspace = app_proc;
	image = aspace->getImage();

/*	BPatch_Set<BPatch_opCode> access_types;
	access_types.insert(BPatch_opLoad);
	access_types.insert(BPatch_opStore);
*/
	vector<BPatch_function *> functions, incr_functions;
	vector<BPatch_point *> *points;
	image->findFunction("function_name", functions);
	points = functions[0]->findPoint(BPatch_entry);

	// create snippet
	image->findFunction("incr", incr_functions);
	vector<BPatch_snippet *> incr_args;
	BPatch_funcCallExpr incr_call(*(incr_functions[0]), incr_args);

	aspace->insertSnippet(incr_call, *points);
	app_proc->continueExecution();
#ifdef __PPC__
	// PPC detach removes snippets, so wait
	bpatch.waitForStatusChange();
#endif
	app_proc->detach(true);

	cout << "MUTATION DONE. MUTATOR IS GOING...\n";

	return 0;
}
